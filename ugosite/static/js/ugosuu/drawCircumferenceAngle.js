JXG.extend(JXG.Board.prototype,  {
    drawCircumferenceAngle: function (){
        var circle = this.create('circle',[[0,0],[0,1]], {strokeWidth:2});
        var pointA = this.create('glider', [1,-1,circle], {name:""} );
        var pointB = this.create('glider', [-1,-1,circle], {name:""});
        var pointP = this.create('point', [
                function(){
                    return Math.cos(window.scrollY/400*3.14)},
                function(){
                    return Math.sin(window.scrollY/400*3.14)},
                ]
            , {name:"P", strokecolor:'orange',fillcolor:'orange',autoPosition: true, offset:[5, 5]}).setAttribute("labelcolor:orange");
        


        var lineAP = this.create('line',[pointA,pointP]);
        var lineBP = this.create('line',[pointB,pointP]);
        var angleAPB = this.createCircumferenceAngle(pointA,pointP,pointB)

        var pointA0 = this.create('mirrorpoint', [pointA ,pointP],{visible:false})
        var pointB0 = this.create('mirrorpoint', [pointB ,pointP],{visible:false})
        var angleA0PB0 = this.createCircumferenceAngle(pointA0,pointP,pointB0)

        var moving_elements=[angleAPB,lineAP,lineBP]

        this.setTraceButtons(moving_elements)

        // スクロール

        window.addEventListener('scroll', ()=> {
            pointP.board.fullUpdate()
            console.log("スクロールを検知！")
            if(window.scrollY%100==0){
                for(let element of moving_elements){
                    element.pause()
                }
            }
        });

        // デザイン
        
        this.select({
            elementClass: JXG.OBJECT_CLASS_POINT,
        }).setAttribute({attractors: [circle], attractorDistance:0.01, snatchDistance: 0.5});

        this.select({
            elementClass: JXG.OBJECT_CLASS_POINT,
            name:""
        }).setAttribute({strokecolor:myTextColor,fillcolor:myTextColor});

        this.select({
            elementClass: JXG.OBJECT_CLASS_LINE,
        }).setAttribute({straightFirst:true, straightLast:true, strokeWidth:2,strokecolor:myTextColor});
        
        this.select({
            elementClass: JXG.OBJECT_CLASS_CIRCLE,
        }).setAttribute({strokecolor:myTextColor});
    }
})

JXG.extend(JXG.Board.prototype,  {
    createCircumferenceAngle: function (arcStart,circumference,arcEnd){
        pointS = this.create('point',[
            function(){return circumference.pointForMajorArc(arcStart,arcEnd).X()},
            function(){return circumference.pointForMajorArc(arcStart,arcEnd).Y()}
        ],{visible:false})
        var angle = this.create('nonreflexangle',[arcStart,circumference,pointS],{
           strokeWidth:2, strokecolor:'orange', orthoSensitivity:10,radius:0.2,fillOpacity:1
        });
        angle.setLabel("")
        return angle
    }
})

JXG.extend(JXG.Point.prototype,  {
    isOnMajorArc: function(arcStart,arcEnd){
        angle = JXG.Math.Geometry.rad(arcEnd,this,arcStart)
        return angle<3.14
    },
    pointForMajorArc: function(arcStart,arcEnd){
        if(this.isOnMajorArc(arcStart,arcEnd)){
            return arcEnd
        }else{
            return arcEnd.board.create('mirrorpoint', [arcEnd ,this],{visible:false})
        }
    },
})