function What(name){
    document.getElementById("hash").getElementsByTagName("h2")[0].innerHTML = name
    document.getElementById("TASL").src = `data/plots/${name}/tasl.png`
    document.getElementById("FINAL").src = `data/plots/${name}/final.png`
    document.getElementById("BULL").src = `data/plots/${name}/Bullish.png`
    document.getElementById("BEAR").src = `data/plots/${name}/Bearish.png`
    
    fetch("data/stats.json")
        .then(response => response.json())
        .then(data => {
            var total_alerts = data[name]["total_alerts"];
            var total_bull = data[name]["total_bull"];
            var total_bear = data[name]["total_bear"];
            var avg_NoD = data[name]["avg_NoD"];
            var total_stagnant = data[name]["total_stagnant"];
            var stag_percent = total_stagnant/total_alerts * 100;
            var bull_percent = total_bull/total_alerts * 100;
            var bear_percent = total_bear/total_alerts * 100;

            document.getElementById("hash").getElementsByTagName("p")[1].innerHTML = `Total Alerts = ${total_alerts}`;
            document.getElementById("nbull").innerHTML = `Total Bullish Alerts = ${total_bull} (${bull_percent.toFixed(2)}% of total alerts)`;
            document.getElementById("nbear").innerHTML = `Total Bearish Alerts = ${total_bear} (${bear_percent.toFixed(2)}% of total alerts)`;
            document.getElementById("nod").innerHTML = `Avg no. of days needed to hit Target = ${avg_NoD.toFixed(2)}`;
            document.getElementById("stagnant").innerHTML = `Total Stagnant alerts = ${total_stagnant} (${stag_percent.toFixed(2)}% of total alerts)`;
                })
}