<script>
export default {
    DataTransfer(){
        items: [{ message: 'Foo' }, { message: 'Bar' }]
    }
}
</script>


<template>
<div class="table">
    <h2>Hier könnte eine Tabelle Stehen :D></h2>
    <div class="table_array">
        <li class="table_row" v-for="(item, index) in items">
            <div class="row_frame">

            </div>
        </li>
    </div>
</div>

</template>


<style>


</style>