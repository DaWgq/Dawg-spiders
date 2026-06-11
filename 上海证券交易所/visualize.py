import csv
import json
import os

csv_path = os.path.join(os.path.dirname(__file__), "etf_data.csv")
html_path = os.path.join(os.path.dirname(__file__), "etf_analysis.html")

data = []
with open(csv_path, "r", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        data.append(
            {
                "date": row["日期"],
                "code": row["基金代码"],
                "name": row["基金简称"],
                "vol": float(row["基金规模（万份）"]),
            }
        )

data.sort(key=lambda x: x["vol"], reverse=True)

total_vol = sum(d["vol"] for d in data)
avg_vol = total_vol / len(data)
max_item = data[0]
min_item = data[-1]
over_million = sum(1 for d in data if d["vol"] >= 1000000)

ranges = [
    ("<1万", 0, 10000),
    ("1-5万", 10000, 50000),
    ("5-10万", 50000, 100000),
    ("10-50万", 100000, 500000),
    ("50-100万", 500000, 1000000),
    ("100-500万", 1000000, 5000000),
    ("500万+", 5000000, float("inf")),
]
dist_data = [
    {"name": label, "value": sum(1 for d in data if lo <= d["vol"] < hi)}
    for label, lo, hi in ranges
]

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>上交所ETF基金规模分析</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f172a; color: #e2e8f0; font-family: 'Microsoft YaHei', sans-serif; padding: 20px; }}
h1 {{ text-align: center; font-size: 28px; margin-bottom: 20px; color: #38bdf8; }}
.dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1600px; margin: 0 auto; }}
.card {{ background: #1e293b; border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
.card h3 {{ font-size: 16px; margin-bottom: 10px; color: #94a3b8; }}
.chart {{ width: 100%; height: 450px; }}
.full {{ grid-column: 1 / -1; }}
.full .chart {{ height: 500px; }}
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; max-width: 1600px; margin: 0 auto 20px; }}
.stat-card {{ background: #1e293b; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
.stat-card .label {{ font-size: 13px; color: #94a3b8; margin-bottom: 8px; }}
.stat-card .value {{ font-size: 24px; font-weight: bold; color: #38bdf8; }}
.stat-card .sub {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
</style>
</head>
<body>

<h1>上海证券交易所 ETF 基金规模数据可视化</h1>

<div class="stats">
    <div class="stat-card"><div class="label">ETF 总数</div><div class="value">{len(data)}</div><div class="sub">上交所上市</div></div>
    <div class="stat-card"><div class="label">总规模（万份）</div><div class="value">{total_vol / 10000:.2f}亿</div><div class="sub">{total_vol:,.0f} 万份</div></div>
    <div class="stat-card"><div class="label">平均规模（万份）</div><div class="value">{avg_vol / 10000:.2f}亿</div><div class="sub">{avg_vol:,.0f} 万份</div></div>
    <div class="stat-card"><div class="label">百万份以上</div><div class="value">{over_million}</div><div class="sub">占比 {over_million / len(data) * 100:.1f}%</div></div>
</div>

<div class="dashboard">
    <div class="card">
        <h3>TOP 20 基金规模排行（万份）</h3>
        <div class="chart" id="chart-top20"></div>
    </div>
    <div class="card">
        <h3>基金规模区间分布</h3>
        <div class="chart" id="chart-dist"></div>
    </div>
    <div class="card full">
        <h3>全部基金规模一览（按规模降序）</h3>
        <div class="chart" id="chart-all"></div>
    </div>
</div>

<script>
var DATA = {json.dumps(data, ensure_ascii=False)};
var DIST = {json.dumps(dist_data, ensure_ascii=False)};

(function() {{
    var top20 = DATA.slice(0, 20);
    var chartTop20 = echarts.init(document.getElementById('chart-top20'));
    chartTop20.setOption({{
        tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
        grid: {{ left: 120, right: 50, top: 10, bottom: 10 }},
        xAxis: {{ type: 'value', name: '万份', axisLabel: {{ formatter: function(v) {{ return (v/10000).toFixed(0)+'亿'; }} }} }},
        yAxis: {{ type: 'category', data: top20.map(function(d){{return d.name;}}).reverse(), inverse: true, axisLabel: {{ fontSize: 11 }} }},
        series: [{{
            type: 'bar', data: top20.map(function(d){{return d.vol;}}).reverse(),
            itemStyle: {{ color: new echarts.graphic.LinearGradient(0,0,1,0,[{{offset:0,color:'#38bdf8'}},{{offset:1,color:'#818cf8'}}]) }},
            label: {{ show: true, position: 'right', fontSize: 10, formatter: function(p){{ return (p.value/10000).toFixed(1)+'亿'; }} }}
        }}]
    }});

    var chartDist = echarts.init(document.getElementById('chart-dist'));
    chartDist.setOption({{
        tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}} 只 ({{d}}%)' }},
        series: [{{
            type: 'pie', radius: ['40%','70%'], center: ['50%','55%'],
            data: DIST,
            label: {{ formatter: '{{b}}\\n{{c}}只', fontSize: 11 }},
            emphasis: {{ label: {{ fontSize: 16, fontWeight: 'bold' }} }},
            itemStyle: {{ borderRadius: 4, borderColor: '#1e293b', borderWidth: 3 }}
        }}]
    }});

    var chartAll = echarts.init(document.getElementById('chart-all'));
    chartAll.setOption({{
        tooltip: {{ trigger: 'axis', formatter: function(p){{ return p[0].name + '<br/>代码: ' + p[0].data[2] + '<br/>规模: ' + p[0].value.toLocaleString() + ' 万份'; }} }},
        grid: {{ left: 80, right: 30, top: 20, bottom: 60 }},
        dataZoom: [{{ type: 'slider', start: 0, end: 100, height: 25, bottom: 10 }}],
        xAxis: {{ type: 'category', data: DATA.map(function(d){{return d.name;}}), axisLabel: {{ show: false }} }},
        yAxis: {{ type: 'value', name: '万份', axisLabel: {{ formatter: function(v){{ return (v/10000).toFixed(0)+'亿'; }} }} }},
        series: [{{
            type: 'scatter',
            data: DATA.map(function(d){{ return [d.name, d.vol, d.code]; }}),
            symbolSize: function(d){{ return Math.max(3, Math.log(d[1])/Math.LN10 * 3); }},
            itemStyle: {{ color: new echarts.graphic.LinearGradient(0,0,0,1,[{{offset:0,color:'#38bdf8'}},{{offset:1,color:'#a78bfa'}}]) }}
        }}]
    }});

    window.addEventListener('resize', function() {{
        chartTop20.resize();
        chartDist.resize();
        chartAll.resize();
    }});
}})();
</script>
</body>
</html>"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"可视化页面已生成: {html_path}")
print(f"共 {len(data)} 条 ETF 数据")
