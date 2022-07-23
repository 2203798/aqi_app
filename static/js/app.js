console.log("js script connected");

/**---------------------------------------------------------
 * GLOBAL VARIABLES (for fields)
 * Accessible and dynamic vars here
 ---------------------------------------------------------*/
// Hourly Forecast
var hourLabels = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00"];
var hourDataset = [10, 20, 30, 40, 35, 60, 50];
// Daily Forecast
var dayLabels = ["MON", "TUE", "WED", "THUR", "FRI", "SAT", "SUN"];
var dayDataset = [10, 20, 30, 40, 35, 60, 50];

var aqi = 0;
// AQI Gauge (Warning: Do not change the values!)
const gaugeDataset = [50, 50, 50, 50, 100, 200];
const gaugeLabels = [
  "Good: 0-50",
  "Fair: 51-100",
  "Unhealthy: 101-150",
  "Very Unhealthy: 151-200",
  "Acutely Unhealty: 201-300",
  "Emergency: 301-500",
];

/**---------------------------------------------------------
 * CHARTS
 * Line and Gauge chart
 ---------------------------------------------------------*/
// Line Chart
function lineChart(element, labels, pred, actual) {
  console.log(typeof labels)
  console.log(typeof pred)
  console.log(typeof actual)
  console.log(labels, pred, actual)
  const ctx = document.getElementById(element).getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Predicted",
          data: pred,
          fill: false,
          borderColor: "rgb(52,89,230)", //75, 192, 192
          tension: 0.5,
        },
        {
          label: "Actual",
          data: actual,
          fill: false,
          borderColor: "rgb(75, 192, 192)", //75, 192, 192
          tension: 0.5,
        }
        
      ],
    },
    options: {
      responsive: false,
      scales: {
        x: {
          position: "top",
          ticks: {
            color: function (context) {
              if (context.tick.label === labels[9]) {
                return "rgb(52,89,230)";
              }
            },
          },
        },
      },
      plugins: {
        legend: {
          display: true,
        },
      },
    },
  });
}
// Gauge Chart
function gaugeChart(element, labels, dataset) {
  const ctx = document.getElementById(element).getContext("2d");
  new Chart(gauge, {
    type: "doughnut",
    data: {
      labels: [
        "Good: 0-50",
        "Fair: 51-100",
        "Unhealthy: 101-150",
        "Very Unhealthy: 151-200",
        "Acutely Unhealty: 201-300",
        "Emergency: 301-500",
      ],
      datasets: [
        {
          //label: "Dataset 1",
          data: dataset,
          needleValue: 10,
          backgroundColor: [
            "rgb(0, 153, 0)",
            "rgb(255, 255, 0)",
            "rgb(228, 108, 9)",
            "rgb(254, 0, 0)",
            "rgb(112, 48, 160)",
            "rgb(107, 43, 43)",
          ],
        },
      ],
    },
    options: {
      circumference: 180,
      rotation: -90,
      cutout: "90%",
      responsive: false,
      // animation: {
      //   duration: 0,
      // },
      plugins: {
        tooltip: {
          intersect: true,
          //enabled: false,
          callbacks: {
            label: (context) => {
              return context.label;
            },
          },
        },
        legend: {
          display: false,
        },
      },
    },
  });
}

/**---------------------------------------------------------
 * HELPER METHODS
 * Additional interactive methods
 ---------------------------------------------------------*/
/**

/**
 * Theta Formula (Customized)
 * s = arc length -> AQI value
 * r = radius
 * Θ = ((s-r)/r)*90
 */
function gaugeMarkerTheta(computedAQI) {
  s = computedAQI; // arc length
  r = 250; // radius
  return ((s - r) / r) * 90;
}

function aqiDesc(aqi) {
  if (aqi >= 0 && aqi <= 50) {
    return "Good";
  } else if (aqi >= 51 && aqi <= 100) {
    return "Fair";
  } else if (aqi >= 101 && aqi <= 150) {
    return "Unhealthy";
  } else if (aqi >= 151 && aqi <= 200) {
    return "Very Unhealthy";
  } else if (aqi >= 201 && aqi <= 300) {
    return "Acutely Unhealthy";
  } else if (aqi >= 301 && aqi <= 500) {
    return "Emergency";
  }
}

// randBtn.addEventListener("click", function () {
//   const aqiElem = document.getElementById("aqi");
//   const aqiDescElem = document.getElementById("aqi-desc");
//   const gaugeMarker = document.getElementById("gaugeMarker");

//   var aqiVal = Math.floor((Math.random() * 500)) + 1;
//   aqiElem.innerText = aqiVal;
//   aqiDescElem.innerHTML = aqiDesc(aqiVal);
//   gaugeMarker.style.transform = "rotate(" + gaugeMarkerTheta(aqiVal) + "deg)";
// });

randBtn.addEventListener("click", function() {
  // 63 expected AQI result
  document.getElementById("pm25").value = 16.40350877;
  document.getElementById("pm10").value = 27.85416667;
  document.getElementById("nox").value = 0;
  document.getElementById("nh3").value = 9.377083333;
  document.getElementById("o3").value = 0.391875;
  document.getElementById("co").value = 63;
  document.getElementById("so2").value = 20.43;

})

/**---------------------------------------------------------
 * METHOD CALL (MAIN)
 * Call all needed methods here
 ---------------------------------------------------------*/
