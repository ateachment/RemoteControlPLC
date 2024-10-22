var angle = 0;
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
    angle += newValue;
    if(angle == 200)
        angle == 0;
    document.getElementById("motor.red").setAttribute("transform", "rotate(" + angle + ",50,50)");
}