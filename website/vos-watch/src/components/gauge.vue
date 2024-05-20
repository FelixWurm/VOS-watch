<script>
// import { getPost } from './../api.js'

export default{
    mounted(){
        console.log("Hello World");
        this.fetch_data();
        this.intervalId = setInterval(this.fetch_data, 30000);
        this.percent = this.percent_in
    },

    methods:{
        change_percent(percent_){
            percent_ = parseFloat(percent_)
            this.percent = percent_.toFixed(1);
            //this.transformRotateValue = ((this.percent_ /200) * 10) + "turn";
        },

        async fetch_data(){
            try {
                await fetch('http://127.0.0.1:5000/', {method:'GET'})
                .then((response) => response.json())
                .then((json) => this.change_percent(json["DELAY"]));
            } catch (error) {
                console.log(error)
            }
        }
    },

    props:{
        percent_in:{
            type:Number,
            required:false
        }
    },
    data(){
        return{
            percent:0.0,
            transformRotateValue:"0.250turn"
        }
    }
}
</script>


<template>
<div class="gauge__outer">
    
    <div class="gauge__inner">
        <div class="gauge__fill" :class="{rotate:transformRotateValue}">
        </div>

        <div class="gauge__cover">
            {{ this.percent }} Minuten
        </div>   

    </div>
</div>
</template>


<style scoped>

.gauge__outer{
    width: 75%;
    /* max-width: 250px; */
}

.gauge__inner{
    width: 100%;
    height: 0;
    padding-bottom: 50%;
    background-color: chocolate;
    position: relative;
    border-top-left-radius: 100% 200%;
    border-top-right-radius: 100% 200%;
    overflow: hidden;
}

.gauge__fill{
    position: absolute;
    top:100%;
    left: 0%;
    width: inherit;
    height: 100%;
    background-color: green;
    transform-origin: center top;
    transform: rotate(0.0turn);
    transition: transform 0.2s ease-out;
}

.gauge__cover{
    position: absolute;

    width: 75%;
    height: 150%;

    top:25%;
    left:50%;

    transform: translateX(-50%);

    border-radius: 50%;

    background-color:black;

    /**Text */
    display: flex;
    align-items: center;
    justify-content: center;
    padding-bottom: 30%;
    box-sizing: border-box;
    color: white;
    font-weight: bold;
    font-size: 25px;
}
</style>