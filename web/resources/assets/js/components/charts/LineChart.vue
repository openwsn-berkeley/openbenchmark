
<script>
    import { Line } from 'vue-chartjs'

    export default {
        extends: Line,

        props: [
            'label',
            'x-axis',
            'y-axis'
        ],

        data: function() {
            return {
                titles: {
                    "latency": "Latency",
                    "reliability": "Reliability",
                    "radioDutyCycle": "Duty Cycle"
                }
            }
        },

        methods: {
            renderLineChart() {
                this.renderChart(
                    {
                        labels: this.xAxis,
                        datasets: [
                            {
                                label: this.label,
                                borderColor: '#6699CC',
                                data: this.yAxis
                            }
                        ]
                    },
                    {   
                        responsive: false,
                        maintainAspectRatio: false,
                        title: {
                            display: true,
                            text: this.titles[this.label]
                        },
                        legend: {
                            display: false
                        },
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }],
                            xAxes: [{
                                ticks: {
                                    autoSKip: false,
                                    stepSize: 100
                                }
                            }]
                        }
                    }
                )
            }
        },

        watch: {
            xAxis: function() {
                this.$data._chart.update();
            }
        },

        mounted () {
            this.renderLineChart();
        }

    }

</script>