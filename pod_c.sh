#!/bin/bash

function on () {
	gpio -g mode 12 pwm
	gpio -g mode 13 pwm
	gpio pwm-ms
	setm 375 1024
}
function off () {
	gpio -g mode 12 in
	gpio -g mode 13 in
}

function setm () {
	gpio pwmc $1
	gpio pwmr $2
}

function rot_v {
	gpio -g pwm 12 $1
}

function rot_h {
	gpio -g pwm 13 $1
}

$1 $2 $3
