
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="GTA Open World Python",
    page_icon="🚗",
    layout="wide"
)

st.title("🏙️ GTA OPEN WORLD PYTHON")
st.caption("Prototipo 3D de mundo abierto | Python + Streamlit")

st.info(
    "Controles: W acelerar | S frenar | A/D girar | "
    "ESPACIO disparar | R reiniciar"
)

game = r"""
<div id="game" style="width:100%;height:650px;position:relative;background:#111">
<div id="hud" style="position:absolute;z-index:2;top:12px;left:12px;
color:white;background:#000a;padding:12px;border-radius:8px;font-family:Arial">
VELOCIDAD: <span id="speed">0</span> km/h<br>
ESTADO: MODO LIBRE<br>
OBJETIVOS: <span id="score">0</span>
</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<script>
const container = document.getElementById("game");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 70, 260);

const camera = new THREE.PerspectiveCamera(
    70, container.clientWidth / container.clientHeight, 0.1, 1000
);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2));

const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(40,80,30);
sun.castShadow = true;
scene.add(sun);

// Suelo
const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(500,500),
    new THREE.MeshStandardMaterial({color:0x397d43})
);
ground.rotation.x = -Math.PI/2;
ground.position.y = -0.1;
ground.receiveShadow = true;
scene.add(ground);

// Carreteras
function road(x,z,w,d) {
    const r = new THREE.Mesh(
        new THREE.BoxGeometry(w,0.12,d),
        new THREE.MeshStandardMaterial({color:0x292929})
    );
    r.position.set(x,0,z);
    scene.add(r);
}

for(let i=-200;i<=200;i+=50){
    road(i,0,12,450);
    road(0,i,450,12);
}

// Edificios
for(let x=-180;x<=180;x+=25){
    for(let z=-180;z<=180;z+=25){
        if(Math.abs(x%50)<12 || Math.abs(z%50)<12) continue;

        const h = 10 + Math.random()*35;

        const building = new THREE.Mesh(
            new THREE.BoxGeometry(12,h,12),
            new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(
                    0.55,0.12,0.35+Math.random()*0.25
                )
            })
        );

        building.position.set(
            x + (Math.random()-0.5)*4,
            h/2,
            z + (Math.random()-0.5)*4
        );

        building.castShadow = true;
        building.receiveShadow = true;
        scene.add(building);
    }
}

// Vehículo
const car = new THREE.Group();

const body = new THREE.Mesh(
    new THREE.BoxGeometry(2.3,0.8,4.5),
    new THREE.MeshStandardMaterial({color:0xff2020,metalness:0.5,roughness:0.3})
);
body.position.y = 0.9;
body.castShadow = true;
car.add(body);

const cabin = new THREE.Mesh(
    new THREE.BoxGeometry(1.8,0.8,2),
    new THREE.MeshStandardMaterial({color:0x222d39,metalness:0.3})
);
cabin.position.set(0,1.65,-0.3);
car.add(cabin);

// Ruedas
const wheels = [];

for(let x of [-1.15,1.15]){
    for(let z of [-1.4,1.4]){
        const wheel = new THREE.Mesh(
            new THREE.CylinderGeometry(0.48,0.48,0.3,20),
            new THREE.MeshStandardMaterial({color:0x111111})
        );
        wheel.rotation.z = Math.PI/2;
        wheel.position.set(x,0.5,z);
        car.add(wheel);
        wheels.push(wheel);
    }
}

car.position.set(0,0,0);
scene.add(car);

// Objetivos
const targets = [];

for(let i=0;i<12;i++){
    const target = new THREE.Mesh(
        new THREE.BoxGeometry(2,2,2),
        new THREE.MeshStandardMaterial({color:0xffcc00})
    );
    target.position.set(
        Math.random()*150-75,1,Math.random()*150-75
    );
    scene.add(target);
    targets.push(target);
}

const keys = {};
let speed = 0;
let steering = 0;
let score = 0;
let lastShot = 0;

window.addEventListener("keydown",e=>{
    keys[e.code] = true;
    if(["Space","ArrowUp","ArrowDown"].includes(e.code)) e.preventDefault();
});
window.addEventListener("keyup",e=>keys[e.code]=false);

function shoot(){
    const bullet = new THREE.Mesh(
        new THREE.SphereGeometry(0.22,8,8),
        new THREE.MeshBasicMaterial({color:0xffff00})
    );

    bullet.position.copy(car.position);
    bullet.position.y += 1;

    const direction = new THREE.Vector3(
        -Math.sin(car.rotation.y),0,-Math.cos(car.rotation.y)
    );

    scene.add(bullet);

    const start = performance.now();

    function moveBullet(){
        bullet.position.addScaledVector(direction,1.8);

        for(let i=targets.length-1;i>=0;i--){
            if(bullet.position.distanceTo(targets[i].position)<2){
                scene.remove(targets[i]);
                targets.splice(i,1);
                score++;
                document.getElementById("score").textContent=score;
                scene.remove(bullet);
                return;
            }
        }

        if(performance.now()-start<2000){
            requestAnimationFrame(moveBullet);
        }else{
            scene.remove(bullet);
        }
    }
    moveBullet();
}

function animate(){
    requestAnimationFrame(animate);

    // Aceleración y frenado
    if(keys["KeyW"]) speed += 0.018;
    if(keys["KeyS"]) speed -= 0.035;

    speed *= 0.985;
    speed = Math.max(-0.8,Math.min(speed,1.5));

    // Dirección
    const turn = (keys["KeyA"]?1:0)-(keys["KeyD"]?1:0);

    if(Math.abs(speed)>0.01){
        car.rotation.y += turn*0.035*Math.sign(speed);
    }

    // Movimiento
    car.position.x -= Math.sin(car.rotation.y)*speed;
    car.position.z -= Math.cos(car.rotation.y)*speed;

    // Rotación de ruedas
    wheels.forEach(w=>w.rotation.x += speed*0.1);

    // Disparos
    if(keys["Space"] && performance.now()-lastShot>300){
        shoot();
        lastShot=performance.now();
    }

    // Reiniciar vehículo
    if(keys["KeyR"]){
        speed=0;
        car.position.set(0,0,0);
        car.rotation.set(0,0,0);
    }

    // Cámara de seguimiento
    const offset = new THREE.Vector3(
        Math.sin(car.rotation.y)*12,
        7,
        Math.cos(car.rotation.y)*12
    );

    const desired = car.position.clone().add(offset);
    camera.position.lerp(desired,0.08);
    camera.lookAt(car.position.x,car.position.y+1,car.position.z);

    document.getElementById("speed").textContent=
        Math.round(Math.abs(speed)*100);

    renderer.render(scene,camera);
}

window.addEventListener("resize",()=>{
    camera.aspect=container.clientWidth/container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth,container.clientHeight);
});

camera.position.set(0,8,12);
animate();
</script>
"""

components.html(game, height=670, scrolling=False)

st.caption("Proyecto experimental. Los gráficos 3D se renderizan con Three.js.")
