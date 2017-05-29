SIZE = 40;
OFF = SIZE/2; //MOUSE OFFSET
B = 0, W = 1;

class Piece {
    constructor (color, x, y) {
        this.pos = {x:x/SIZE, y:y/SIZE};
        this.color = color;
        this.x = x;
        this.y = y;
        this._orig_pos = {x, y};
        this.mouseDragged = function() { console.log(this, mouseX, mouseY) };
    }
    dropPos () {
        this.pos.x = int((this.x + OFF)/SIZE), this.pos.y = int((this.y + OFF)/SIZE);
        this.x = this.pos.x * SIZE;
        this.y = this.pos.y * SIZE;
        console.log(this.pos, this.x, this.y);
        this._orig_pos = {x:this.x, y:this.y};
    }
    revertPos() {
        this.x = this._orig_pos.x;
        this.y = this._orig_pos.y;
    }
    moveTo (x, y) {
        this.x = x;
        this.y = y;
    }
    draw () {
        const color = this.color === B ? 'black' : 'white';
        push();
        noStroke();
        if (this === currentElement) {
            fill('gray');
        } else { fill(color); }
        translate(OFF, OFF);
        ellipse(this.x, this.y, SIZE);
        pop();
    }

}

var blackPieces = [];
for (let row = 0; row < 10; row++) {
    for (let col = 0; col < 4; col++) {
        if ((row + col) % 2 === 1) {
            blackPieces.push(new Piece(B, row*SIZE, col*SIZE));
        }
    }
}


var whitePieces = [];
for (let i = 0; i < 10; i++) {
    for (let j = 9; j > 5; j--) {
        if ((i + j) % 2 === 1) {
            whitePieces.push(new Piece(W, i*SIZE, j*SIZE));
        }
    }
}

function setup() {
    createCanvas(401, 401);
}

function draw() {
    background("FFF");
    drawBoard();
    drawPieces();
    push();
    fill('green');
    ellipse(mouseX, mouseY, 3);
    pop();
}

function drawPieces() {
    for (let black of blackPieces) {
        black.draw();
    }
    for (let white of whitePieces) {
        white.draw();
        // console.log(white);
    }
}

function drawBoard() {
    const color1 = 'brown', color2 = 'yellow';

    for(let i = 0; i < 10; i++) {
        for(let j = 0; j < 10; j++) {
            let {x, y} = {x: SIZE * i, y: SIZE * j};
            fill((i+j) % 2 == 0 ? color2:color1);
            rect(x, y, SIZE, SIZE);
        }
    }
}


let currentElement = null;
let currentPlayer = W;

function distance(x, y, a, b) {
    return sqrt(pow(x-a, 2) + pow(y - b, 2));
}



function mouseDist(x, y) { return distance(x, y, mouseX, mouseY) }


function mousePressed () {
    console.log('pressed', mouseX, mouseY);
    let col = currentPlayer == W ? whitePieces : blackPieces;
    currentElement = _.find(col, (p) => mouseDist(p.x+OFF, p.y+OFF) < OFF);
}

function mouseReleased() {
    if (!currentElement) { return; }
    console.log('released', mouseX, mouseY);
    // currentElement.revertPos();
    currentElement.dropPos();
    currentElement = null;

}

function mouseDragged () {
    if (!currentElement) { return; }
    currentElement.moveTo(mouseX-OFF, mouseY-OFF);
}



(function () {
    
})();
