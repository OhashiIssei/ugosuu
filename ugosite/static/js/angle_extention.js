function circumferenceAngle(arcStart,circumference,arcEnd){
    function point(p1,p2,p3){
        angle = JXG.Math.Geometry.rad(p3,p2,p1)
        p30 = board.create('mirrorpoint', [p3 ,p2],{visible:false})
        return angle>3.14 ? p3 :p30
    }
    function angleStart_x(){
        return point(arcEnd,circumference,arcStart).X()
    }
    function angleStart_y(){
        return point(arcEnd,circumference,arcStart).Y()
    }
    var angleStart = board.create('point',[angleStart_x,angleStart_y],{name:"S",visible:false})
    var angle = board.create('nonreflexangle',["S",circumference,arcEnd],{
       strokeWidth:2, strokecolor:'orange', orthoSensitivity:10,radius:0.2,fillOpacity:1
    }).setLabel("");
    return angle
}