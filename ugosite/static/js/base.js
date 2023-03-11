myTextColor = 'white'

function base_board(divId){
    return JXG.JSXGraph.initBoard(divId, 
        {
            boundingbox: [-1.2, 1.2, 1.2, -1.2],
            axis:false,
            grid:false,
            showcopyright: false,
            showFullscreen: true,
            fullscreen:{
                symbol: '\u22c7',
                scale: 0.95
            },
        }
    )
}



JXG.extend(JXG.GeometryElement.prototype,  {
    pause: function () {
        this.setAttribute({trace:true})
        this.setAttribute({trace:"pause"})
    }
})

JXG.extend(JXG.Board.prototype,  {
    backGroundcolor: function (color) {
        back = this.create('polygon',[[0.5,0.5],[0.5,-0.5],[-0.5,-0.5],[-0.5,0.5]], {fixed:true,fillOpacity:1,fillcolor:color});
        back.pause()
        back.remove()
        return this
    }
})

JXG.extend(JXG.Board.prototype,  {
    setTraceButtons: function (moving_elements) {
        this.create('button', [0.8, 1, 'trace!', function() {
            for(let element of moving_elements){
                element.pause()
            }
        }], {});
        
        this.create('button', [0.8, 0.8, 'clear!', function() {
            this.board.clearTraces()
        }], {});
    }
})




