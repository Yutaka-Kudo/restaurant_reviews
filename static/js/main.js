"use strict";

console.log(Vue.version);


var dd = new Date();
document.getElementById('id1').innerHTML = dd.toLocaleString();
document.write(dd.toLocaleString());
window.onload = () => {
    setInterval(() => {
        var doc = document.getElementById('id1')
        var dd = new Date();
        doc.innerHTML = dd.toLocaleString();
    }, 1000);
}

function move() { window.find(); console.log('move'); }


var app2 = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app-2",
    watch: {
        message: function (newVal, oldVal) {
            this.error.require = (newVal.length < 1) ? true : false;
            this.error.tooLong = (newVal.length > 5) ? true : false;
            this.oldmsg = oldVal;

        }
    },
    data: {
        message: "xxxsssssss",
        oldmsg: "aaa",
        error: {
            require: false,
            tooLong: false,
        }
    }
})

var app103 = new Vue({
    el: '#app-103',
    data: { seen: true },
    methods: {
        change: function (e) {
            this.seen = e.target.checked
        }
    }
})


Vue.component('my-heading-212', {
    render: function (createE) {
        return createE('h' + this.leve, this.$slots.default)
    },
    props: ['leve']
})
var app212 = new Vue({
    el: '#app-212',
})

let app21212 = document.getElementById('app-212')
let createh1 = document.createElement('h1', "")
var newContent = document.createTextNode("Hi there and greetings!");
app21212.appendChild(createh1)
createh1.appendChild(newContent)









