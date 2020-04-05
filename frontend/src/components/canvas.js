import { fabric } from "fabric"
import chroma from "chroma-js"

function textColor(background) {
  if (chroma(background).get("lab.l") > 70) {
    return chroma("black").hex()
  } else {
    return chroma("white").hex()
  }
}

function createPoint(x, y, color, label) {
  const circle = new fabric.Circle({
    fill: color,
    radius: 6,
    stroke: "black",
  })
  circle.setShadow("2px 2px 2px rgba(0, 0, 0, 0.4)")
  const text = new fabric.Text(label, {
    fontFamily: "Roboto",
    fill: textColor(color),
    fontSize: 13,
    top: 1,
    left: 2,
  })
  const group = new fabric.Group([circle, text], {
    left: x,
    top: y,
    originX: "center",
    originY: "center",
    lockRotation: true,
    lockScalingX: true,
    lockScalingY: true,
    hasControls: false,
    hasBorders: false,
  })
  return group
}

export { createPoint }
