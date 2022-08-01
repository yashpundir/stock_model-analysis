function fo(){
    document.getElementById("hash").getElementsByTagName("h2")[0].innerHTML = "F&O"
    document.getElementById("hash").getElementsByTagName("p")[0].innerHTML = `Data considered for evaluation -> <b>01 Aug, 22</b> to <b>${dd} ${mm},${yyyy}</b>`;
    document.getElementById("TASL").src = "data/plots/FO/tasl.png"
    document.getElementById("FINAL").src = "data/plots/FO/final.png"
    document.getElementById("BULL").src = "data/plots/FO/Bullish.png"
    document.getElementById("BEAR").src = "data/plots/FO/Bearish.png"

    fetch("data/stats.json")
        .then(response => response.json())
        .then(data => {
            var total_alerts = data["FO"]["total_alerts"];
            var total_bull = data["FO"]["total_bull"];
            var total_bear = data["FO"]["total_bear"];
            var avg_NoD = data["FO"]["avg_NoD"];
            var total_stagnant = data["FO"]["total_stagnant"];
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

function ncash(){
    document.getElementById("hash").getElementsByTagName("h2")[0].innerHTML = "NCASH"
    document.getElementById("hash").getElementsByTagName("p")[0].innerHTML = `Data considered for evaluation -> <b>01 Aug, 22</b> to <b>${dd} ${mm},${yyyy}</b>`;
    document.getElementById("TASL").src = "data/plots/Cash_N500/tasl.png"
    document.getElementById("FINAL").src = "data/plots/Cash_N500/final.png"
    document.getElementById("BULL").src = "data/plots/Cash_N500/Bullish.png"
    document.getElementById("BEAR").src = "data/plots/Cash_N500/Bearish.png"

    fetch("data/stats.json")
        .then(response => response.json())
        .then(data => {
            var total_alerts = data["Cash_N500"]["total_alerts"];
            var total_bull = data["Cash_N500"]["total_bull"];
            var total_bear = data["Cash_N500"]["total_bear"];
            var avg_NoD = data["Cash_N500"]["avg_NoD"];
            var total_stagnant = data["Cash_N500"]["total_stagnant"];
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

function ncash_other(){
    document.getElementById("hash").getElementsByTagName("h2")[0].innerHTML = "Cash_Other_N500"
    document.getElementById("hash").getElementsByTagName("p")[0].innerHTML = `Data considered for evaluation -> <b>01 Aug, 22</b> to <b>${dd} ${mm},${yyyy}</b>`;
    document.getElementById("TASL").src = "plots/Cash_Other_N500/tasl.png"
    document.getElementById("FINAL").src = "plots/Cash_Other_N500/final.png"
    document.getElementById("BULL").src = "plots/Cash_Other_N500/Bullish.png"
    document.getElementById("BEAR").src = "plots/Cash_Other_N500/Bearish.png"

    fetch("data/stats.json")
        .then(response => response.json())
        .then(data => {
            var total_alerts = data["Cash_Other_N500"]["total_alerts"];
            var total_bull = data["Cash_Other_N500"]["total_bull"];
            var total_bear = data["Cash_Other_N500"]["total_bear"];
            var avg_NoD = data["Cash_Other_N500"]["avg_NoD"];
            var total_stagnant = data["Cash_Other_N500"]["total_stagnant"];
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

function rtp(){
    document.getElementById("hash").getElementsByTagName("h2")[0].innerHTML = "BO_Rising_Triangle"
    document.getElementById("hash").getElementsByTagName("p")[0].innerHTML = `Data considered for evaluation -> <b>01 Aug, 22</b> to <b>${dd} ${mm},${yyyy}</b>`;
    document.getElementById("TASL").src = "data/plots/BO_Rising_Triangle/tasl.png"
    document.getElementById("FINAL").src = "data/plots/BO_Rising_Triangle/final.png"
    document.getElementById("BULL").src = "data/plots/BO_Rising_Triangle/Bullish.png"
    document.getElementById("BEAR").src = "data/plots/BO_Rising_Triangle/Bearish.png"

    fetch("data/stats.json")
        .then(response => response.json())
        .then(data => {
            var total_alerts = data["BO_Rising_Triangle"]["total_alerts"];
            var total_bull = data["BO_Rising_Triangle"]["total_bull"];
            var total_bear = data["BO_Rising_Triangle"]["total_bear"];
            var avg_NoD = data["BO_Rising_Triangle"]["avg_NoD"];
            var total_stagnant = data["BO_Rising_Triangle"]["total_stagnant"];
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