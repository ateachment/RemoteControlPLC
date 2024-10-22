var ankle = 0;
var rotationInterval;

function initLights(motorschuetz, motorschutzschalter)
{
  if (motorschuetz == 1)
  {
    var element = document.getElementById("motorschuetz");
    element.classList.toggle("on");
    rotationIntervall = setInterval(function () { rotateMotor(20); }, 50);
  }
  if (motorschutzschalter == 0)  //  normally closed
  {
    var element = document.getElementById("motorschutzschalter");
    element.classList.toggle("on");
    clearInterval(rotationInterval);
  }
}
function rotateMotor(newValue)   // rotate motor
{
    ankle += newValue;
    if(ankle == 200)
        ankle == 0;
    document.getElementById("motor.red").setAttribute("transform", "rotate(" + ankle + ",50,50)");
}
