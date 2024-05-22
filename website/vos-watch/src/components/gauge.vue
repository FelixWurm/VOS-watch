<script>
// import { getPost } from './../api.js'

export default{
    mounted(){
        console.log("Hello World");
        this.fetch_data();
        this.intervalId = setInterval(this.fetch_data, 30000);
        if(this.value_in){
            this.value = this.value_in
        }
    },

    methods:{
        change_value(delay,value_green, value_orange, total){
            const parts = delay.split(':');
            const minutes = parseInt(parts[1], 10);
            const secondsParts = parts[2].split('.');
            const seconds = parseInt(secondsParts[0], 10);

            this.value = `${minutes}:${secondsParts[0]}`

            this.transformRotateValue_orange = ((parseFloat(value_orange) + parseFloat(value_green)) / (total*2) ) + "turn";
            this.transformRotateValue_green = (parseFloat(value_green) /(2*total)) + "turn";
        },

        async fetch_data(){
            try {
                await fetch('http://127.0.0.1:5000/', {method:'GET'})
                .then((response) => response.json())
                .then((json) => this.change_value(json["DELAY"],json["C0_3"],json["C3_8"],json["ATA"]));
            } catch (error) {
                console.log(error)
            }
        }
    },

    props:{
        value_in:{
            type:Number,
            required:false
        },
        max_value:{
            type:Number,
            required:false
        }
    },
    data(){
        return{
            value:0.0,
            transformRotateValue_orange:"0.250turn",
            transformRotateValue_green:"0.15turn"
        }
    }
}
</script>


<template>
<div class="gauge__outer">
    
    <div class="gauge__inner">

        <Transition>
            <div class="gauge__fill_orange" :style="{rotate:transformRotateValue_orange}"></div>
        </Transition>
        
        <Transition>
            <div class="gauge__fill_green" :style="{rotate:transformRotateValue_green}"></div>
        </Transition>
        
        <div class="gauge__cover">
            <div class="min_text">
                {{ this.value }} Minuten
            </div>

            <div class = "information_text">
                <span style="color:green"> 0-3 </span>
                <span style="color:orange"> 3-8 </span>
                <span style="color:red"> 8+ </span>
            </div>                 
        </div>  



    </div>
</div>
</template>


<style scoped>

@import '../assets/base.css';
.gauge__outer{
    width: 75%;
    /* max-width: 250px; */
}

.gauge__inner{
    width: 100%;
    height: 0;
    padding-bottom: 50%;
    background-color: red;
    position: relative;
    border-top-left-radius: 100% 200%;
    border-top-right-radius: 100% 200%;
    overflow: hidden;
}

.gauge__fill_green{
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

.gauge__fill_orange{
    position: absolute;
    top:100%;
    left: 0%;
    width: inherit;
    height: 100%;
    background-color: orange;
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

    background-color:var(--color-background);
}

.min_text{
    position: relative;
    text-align: center;
    margin-top: 18%;

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

.information_text{
    height: 40%;
    font-size: 130%;
    margin-top: -30%;

    align-items: center;
    text-align: center;
    word-spacing: 150%;

}
</style>