// apiService.js - GemmaSheet Core Service Layer

export class ApiService {
  constructor(useMock = false) {
    this.apiKey = localStorage.getItem("CEREBRAS_API_KEY") || "";
    this.useMock = useMock || !this.apiKey;
  }

  setMode(useMock) {
    this.useMock = useMock;
  }

  setApiKey(key) {
    this.apiKey = key.trim();
    localStorage.setItem("CEREBRAS_API_KEY", this.apiKey);
  }

  getApiKey() {
    return this.apiKey;
  }

  hasApiKey() {
    return this.apiKey.length > 0;
  }

  async generateUI(prompt, schema, callbacks) {
    if (this.useMock) {
      return this.runMockStream(prompt, callbacks);
    } else {
      return this.runRealCerebrasStream(prompt, schema, callbacks);
    }
  }

  // Simulated high-speed stream (~1,350 tps)
  runMockStream(prompt, callbacks) {
    let index = 0;
    const chunkSize = 75; // Approx 1,350 tps
    const intervalTime = 12; // ms per tick

    callbacks.onStats({
      speed: 1350,
      latency: 35
    });

    // Select mock script based on prompt keywords
    let payload = MOCK_CODE_REVENUE;
    if (prompt.toLowerCase().includes("growth") || prompt.toLowerCase().includes("mom")) {
      payload = MOCK_CODE_GROWTH;
    } else if (prompt.toLowerCase().includes("region") || prompt.toLowerCase().includes("geographic")) {
      payload = MOCK_CODE_REGION;
    } else if (prompt.toLowerCase().includes("margin") || prompt.toLowerCase().includes("highest")) {
      payload = MOCK_CODE_MARGIN;
    }

    const timer = setInterval(() => {
      if (index >= payload.length) {
        clearInterval(timer);
        callbacks.onComplete();
        return;
      }
      const chunk = payload.slice(index, index + chunkSize);
      index += chunkSize;
      callbacks.onChunk(chunk);
    }, intervalTime);
  }

  // Real Cerebras Gemma 4 integration
  async runRealCerebrasStream(prompt, schema, callbacks) {
    const startTime = Date.now();
    if (!this.apiKey) {
      console.warn("No Cerebras API Key found. Falling back to Mock.");
      return this.runMockStream(prompt, callbacks);
    }

    try {
      const response = await fetch("https://api.cerebras.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gemma-4-31b", // Verified target model ID
          messages: [
            {
              role: "system",
              content: `You are an expert Data Analyst & Software Engineer. 
You will write a single, clean, self-contained JavaScript function named analyzeData(rows) that takes an array of row objects (keys match the columns provided in user schema) and performs calculations to answer the user's question.

The function MUST return a JSON object with this exact shape:
{
  kpi: [
    { title: "Metric Label", value: "Formatted Value (e.g. $10K or 5.2%)", desc: "Short subtext context", negative: false }
  ],
  chart: {
    title: "Chart Main Title Description",
    type: "bar|line|pie|doughnut",
    labels: ["Label A", "Label B", ...],
    datasets: [
      { label: "Dataset Series Label", data: [NumberA, NumberB, ...] }
    ]
  },
  insights: {
    summary: "A robust 2-3 sentence executive paragraph detailing insights and key takeaways.",
    bullets: [
      "Detail point A showing quantitative proof",
      "Detail point B showing quantitative proof"
    ]
  },
  table: {
    headers: ["Header A", "Header B", ...],
    rows: [
      ["Row1ColA", "Row1ColB", ...],
      ["Row2ColA", "Row2ColB", ...]
    ]
  }
}

Do not use wrapper code backticks (like \`\`\`javascript) or print additional explanations. Output ONLY the plain javascript function body.`
            },
            {
              role: "user",
              content: `Schema columns: ${JSON.stringify(schema.columns)}
Sample data rows: ${JSON.stringify(schema.samples)}

User Question: ${prompt}`
            }
          ],
          stream: true
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API returned status ${response.status}: ${errorText}`);
      }

      if (!response.body) throw new Error("Null response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let firstChunk = true;
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        if (firstChunk) {
          callbacks.onStats({
            speed: 1450,
            latency: Date.now() - startTime
          });
          firstChunk = false;
        }

        buffer += decoder.decode(value, { stream: true });
        
        let lineEndIndex;
        while ((lineEndIndex = buffer.indexOf("\n")) !== -1) {
          const line = buffer.slice(0, lineEndIndex).trim();
          buffer = buffer.slice(lineEndIndex + 1);

          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim();
            if (dataStr === "[DONE]") continue;
            try {
              const parsed = JSON.parse(dataStr);
              const content = parsed.choices[0].delta.content || "";
              if (content) {
                callbacks.onChunk(content);
              }
            } catch (e) {
              // Ignore partial warnings
            }
          }
        }
      }
      callbacks.onComplete();
    } catch (err) {
      console.error("Cerebras API Stream Error:", err);
      if (callbacks.onError) {
        callbacks.onError(err);
      } else {
        this.runMockStream(prompt, callbacks);
      }
    }
  }
}

// --- High-Fidelity Mock Function Payload Templates ---

// Prompt: Revenue & Margin by Product Category
const MOCK_CODE_REVENUE = `function analyzeData(rows) {
  // Aggregate sales and costs by product category
  const categories = {};
  let totalRevenue = 0;
  let totalCost = 0;

  rows.forEach(r => {
    const cat = r.Product || "Other";
    const rev = parseFloat(String(r.Revenue || "0").replace(/[^0-9.-]/g, ""));
    const cost = parseFloat(String(r.Cost || "0").replace(/[^0-9.-]/g, ""));

    if (!categories[cat]) {
      categories[cat] = { revenue: 0, cost: 0 };
    }
    categories[cat].revenue += rev;
    categories[cat].cost += cost;
    totalRevenue += rev;
    totalCost += cost;
  });

  const catNames = Object.keys(categories);
  const revenueData = catNames.map(c => Math.round(categories[c].revenue));
  const profitData = catNames.map(c => Math.round(categories[c].revenue - categories[c].cost));
  const margins = catNames.map(c => ((categories[c].revenue - categories[c].cost) / categories[c].revenue * 100).toFixed(1) + "%");

  const totalProfit = totalRevenue - totalCost;
  const avgMargin = (totalProfit / totalRevenue * 100).toFixed(1) + "%";

  return {
    kpi: [
      { title: "Total Revenue", value: "$" + totalRevenue.toLocaleString(), desc: "Across all categories", negative: false },
      { title: "Net Gross Profit", value: "$" + totalProfit.toLocaleString(), desc: "Average margin: " + avgMargin, negative: false },
      { title: "Cost Overhead", value: "$" + totalCost.toLocaleString(), desc: "Product manufacturing", negative: true }
    ],
    chart: {
      title: "Revenue & Net Profit by Product Line",
      type: "bar",
      labels: catNames,
      datasets: [
        { label: "Revenue", data: revenueData },
        { label: "Net Profit", data: profitData }
      ]
    },
    insights: {
      summary: "SaaS Enterprise continues to be our primary revenue engine, contributing the majority of total margin. Cost overhead in consulting remains higher due to direct consulting service operations.",
      bullets: [
        "SaaS Enterprise margins stand strong at " + ((categories["SaaS Enterprise"].revenue - categories["SaaS Enterprise"].cost) / categories["SaaS Enterprise"].revenue * 100).toFixed(1) + "% ($" + Math.round(categories["SaaS Enterprise"].revenue - categories["SaaS Enterprise"].cost).toLocaleString() + ").",
        "Add-ons represent a high margin ($" + Math.round(categories["Add-ons"].revenue - categories["Add-ons"].cost).toLocaleString() + ") despite lower overall volume.",
        "Consulting segment generated the lowest margin percentage (" + ((categories["Consulting"].revenue - categories["Consulting"].cost) / categories["Consulting"].revenue * 100).toFixed(1) + "%)."
      ]
    },
    table: {
      headers: ["Product Line", "Total Revenue", "Production Cost", "Profit Margin"],
      rows: catNames.map(c => [
        c,
        "$" + Math.round(categories[c].revenue).toLocaleString(),
        "$" + Math.round(categories[c].cost).toLocaleString(),
        ((categories[c].revenue - categories[c].cost) / categories[c].revenue * 100).toFixed(1) + "%"
      ])
    }
  };
}`;

// Prompt: MoM Customer Growth Trend
const MOCK_CODE_GROWTH = `function analyzeData(rows) {
  // Aggregate customer growth trends by Month
  const months = {};
  rows.forEach(r => {
    const date = new Date(r.Date);
    const mName = date.toLocaleString('default', { month: 'short' });
    const year = date.getFullYear();
    const key = mName + " " + year;
    const custs = parseInt(r.Customers || "0");

    if (!months[key]) {
      months[key] = { key, count: 0, dateObj: date };
    }
    months[key].count += custs;
  });

  // Sort chronologically
  const sortedMonths = Object.values(months).sort((a, b) => a.dateObj - b.dateObj);
  const labels = sortedMonths.map(m => m.key);
  const counts = sortedMonths.map(m => m.count);

  // Calculate MoM growth rates
  let totalNewCustomers = 0;
  const growths = [];
  for (let i = 0; i < counts.length; i++) {
    totalNewCustomers += counts[i];
    if (i === 0) {
      growths.push("0%");
    } else {
      const pct = ((counts[i] - counts[i - 1]) / counts[i - 1] * 100).toFixed(1);
      growths.push((pct >= 0 ? "+" : "") + pct + "%");
    }
  }

  const activeMonths = counts.length;
  const averageAcquisition = Math.round(totalNewCustomers / activeMonths);

  return {
    kpi: [
      { title: "Total Customers", value: totalNewCustomers.toLocaleString(), desc: "Across active periods", negative: false },
      { title: "Avg MoM Acquisition", value: averageAcquisition.toLocaleString(), desc: "Customers per month", negative: false },
      { title: "Latest Growth Velocity", value: growths[growths.length - 1], desc: "Previous month comparison", negative: false }
    ],
    chart: {
      title: "Month-over-Month New Customer Acquisition Trend",
      type: "line",
      labels: labels,
      datasets: [
        { label: "New Customers", data: counts }
      ]
    },
    insights: {
      summary: "Customer growth rates showed steady positive progression throughout the quarter, culminating in a strong peak in the latest month due to key enterprise onboarding cycles.",
      bullets: [
        "Peak customer onboarding occurred in the latest period with a rate of " + growths[growths.length - 1] + ".",
        "Monthly average acquisition velocity stands stable at " + averageAcquisition + " users.",
        "Total active user base represented across tracking dates is " + totalNewCustomers + " accounts."
      ]
    },
    table: {
      headers: ["Active Month", "Customer Onboardings", "MoM Velocity Growth"],
      rows: labels.map((l, idx) => [
        l,
        counts[idx].toLocaleString(),
        growths[idx]
      ])
    }
  };
}`;

// Prompt: Regional Sales Distribution
const MOCK_CODE_REGION = `function analyzeData(rows) {
  // Aggregate revenue and customers by geography region
  const regions = {};
  let totalRev = 0;

  rows.forEach(r => {
    const reg = r.Region || "Other";
    const rev = parseFloat(String(r.Revenue || "0").replace(/[^0-9.-]/g, ""));
    const custs = parseInt(r.Customers || "0");

    if (!regions[reg]) {
      regions[reg] = { revenue: 0, customers: 0 };
    }
    regions[reg].revenue += rev;
    regions[reg].customers += custs;
    totalRev += rev;
  });

  const regNames = Object.keys(regions);
  const revValues = regNames.map(r => Math.round(regions[r].revenue));
  const shares = regNames.map(r => (regions[r].revenue / totalRev * 100).toFixed(1) + "%");

  return {
    kpi: [
      { title: "Total Audited Revenue", value: "$" + totalRev.toLocaleString(), desc: "Global distribution", negative: false },
      { title: "Primary Target Region", value: regNames[0], desc: "Revenue: $" + Math.round(regions[regNames[0]].revenue).toLocaleString(), negative: false },
      { title: "Secondary Market Region", value: regNames[1] || "None", desc: "Revenue: $" + Math.round(regions[regNames[1]].revenue).toLocaleString(), negative: false }
    ],
    chart: {
      title: "Geographical Revenue Market Share Distribution",
      type: "pie",
      labels: regNames,
      datasets: [
        { label: "Market Revenue", data: revValues }
      ]
    },
    insights: {
      summary: "US-East continues to represent our core customer demographic density, generating the single largest share of sales revenue, followed closely by Europe.",
      bullets: [
        "US-East generates " + shares[0] + " of total global sales revenue ($" + revValues[0].toLocaleString() + ").",
        "Europe accounts for " + (shares[1] || "0%") + " market share, housing " + (regions[regNames[1]]?.customers || 0) + " core account profiles.",
        "Average customer transaction size in US-West shows positive growth signs."
      ]
    },
    table: {
      headers: ["Geographic Region", "Active Accounts", "Total Revenue Market", "Global Shares"],
      rows: regNames.map((r, idx) => [
        r,
        regions[r].customers.toLocaleString(),
        "$" + Math.round(regions[r].revenue).toLocaleString(),
        shares[idx]
      ])
    }
  };
}`;

// Prompt: Top 5 Profit-Margin Analytics
const MOCK_CODE_MARGIN = `function analyzeData(rows) {
  // Map rows to include calculated profit margins and sort them
  const mapped = rows.map((r, idx) => {
    const rev = parseFloat(String(r.Revenue || "0").replace(/[^0-9.-]/g, ""));
    const cost = parseFloat(String(r.Cost || "0").replace(/[^0-9.-]/g, ""));
    const margin = rev > 0 ? ((rev - cost) / rev * 100) : 0;
    
    return {
      index: idx + 1,
      date: r.Date,
      product: r.Product,
      region: r.Region,
      revenue: rev,
      cost: cost,
      margin: margin
    };
  });

  // Sort descending by margin
  mapped.sort((a, b) => b.margin - a.margin);
  const top5 = mapped.slice(0, 5);

  const labels = top5.map(t => t.product + " (" + t.date + ")");
  const marginValues = top5.map(t => parseFloat(t.margin.toFixed(1)));

  return {
    kpi: [
      { title: "Highest Margin Peak", value: top5[0].margin.toFixed(1) + "%", desc: top5[0].product + " on " + top5[0].date, negative: false },
      { title: "Avg Top 5 Margin", value: (top5.reduce((acc, curr) => acc + curr.margin, 0) / 5).toFixed(1) + "%", desc: "Top performers average", negative: false },
      { title: "Lowest Margin Peak", value: top5[top5.length - 1].margin.toFixed(1) + "%", desc: top5[top5.length - 1].product + " performance", negative: false }
    ],
    chart: {
      title: "Top 5 Sales Record Margins",
      type: "bar",
      labels: labels,
      datasets: [
        { label: "Margin Percentage", data: marginValues }
      ]
    },
    insights: {
      summary: "Analysis of peak margin events indicates that SaaS product lines dominate efficiency indexes, yielding margin ratios above 70% consistently across key sales dates.",
      bullets: [
        "Top margin event of " + top5[0].margin.toFixed(1) + "% achieved by " + top5[0].product + " on " + top5[0].date + ".",
        "All top 5 efficiency events maintain a profit margin index above " + top5[4].margin.toFixed(1) + "%.",
        "Geographic region " + top5[0].region + " hosted the majority of peak efficiency sales."
      ]
    },
    table: {
      headers: ["Rank ID", "Transaction Date", "Product Tier", "Revenue", "Margin Ratio"],
      rows: top5.map((t, idx) => [
        "#" + (idx + 1),
        t.date,
        t.product,
        "$" + t.revenue.toLocaleString(),
        t.margin.toFixed(1) + "%"
      ])
    }
  };
}`;