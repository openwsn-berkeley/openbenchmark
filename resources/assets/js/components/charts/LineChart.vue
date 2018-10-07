
<script>
    import { Line } from 'vue-chartjs'

    export default {
        extends: Line,

        props: [
            'label',
            'x-axis',
            'y-axis'
        ],

        methods: {
            renderLineChart() {
                this.renderChart(
                    {
                        labels: this.xAxis,
                        datasets: [
                            {
                                label: this.label,
                                backgroundColor: '#6699CC',
                                data: this.yAxis
                            }
                        ]
                    },
                    {
                        responsive: false,
                        maintainAspectRatio: false
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