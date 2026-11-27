import * as THREE from 'three';

// A common camera is expressed in the parcel's own coordinates. Both physical
// worlds keep their geometry, occlusion and shadows while their parcel projects
// to the same silhouette throughout the handoff.
export function createParcelContinuity(){
  const cache=new WeakMap();
  const common={position:new THREE.Vector3(),target:new THREE.Vector3(),up:new THREE.Vector3(),key:new THREE.Vector3(),fill:new THREE.Vector3(),keyColor:new THREE.Color(),fillColor:new THREE.Color(),skyColor:new THREE.Color(),groundColor:new THREE.Color(),fogColor:new THREE.Color()};
  const sphericalA=new THREE.Spherical(),sphericalB=new THREE.Spherical(),spherical=new THREE.Spherical();
  const tmp=new THREE.Vector3(),savedUp=new THREE.Vector3();
  const cornerA=Array.from({length:8},()=>new THREE.Vector3()),cornerB=Array.from({length:8},()=>new THREE.Vector3());
  const corners=Array.from({length:8},(_,i)=>new THREE.Vector3(i&1?1.2:-1.2,i&2?.8:-.8,i&4?.85:-.85));
  const anchor=new THREE.Vector2(.62,.52),size=new THREE.Vector2(.15,.2);
  let metrics={active:false},activeA=null,activeB=null;
  const mix=(a,b,p)=>a+(b-a)*p;
  function state(world){
    let s=cache.get(world);if(s)return s;
    const hemi=world.scene.children.find(o=>o.isHemisphereLight);
    s={world,hemi,parcel:null,position:new THREE.Vector3(),rotation:new THREE.Quaternion(),inverse:new THREE.Quaternion(),scale:new THREE.Vector3(),relative:new THREE.Vector3(),target:new THREE.Vector3(),up:new THREE.Vector3(),key:new THREE.Vector3(),fill:new THREE.Vector3(),keyPosition:new THREE.Vector3(),keyTarget:new THREE.Vector3(),fillPosition:new THREE.Vector3(),fillTarget:new THREE.Vector3(),keyColor:new THREE.Color(),fillColor:new THREE.Color(),skyColor:new THREE.Color(),groundColor:new THREE.Color(),fogColor:new THREE.Color()};
    cache.set(world,s);return s;
  }
  function capture(world){
    const s=state(world),parcel=world.storyParcel;if(!parcel)return null;s.parcel=parcel;
    world.scene.updateMatrixWorld(true);world.camera.updateMatrixWorld(true);
    parcel.getWorldPosition(s.position);parcel.getWorldQuaternion(s.rotation);parcel.getWorldScale(s.scale);s.unit=Math.max(.001,(s.scale.x+s.scale.y+s.scale.z)/3);s.inverse.copy(s.rotation).invert();
    s.relative.copy(world.camera.position).sub(s.position).applyQuaternion(s.inverse).divideScalar(s.unit);
    s.target.copy(world.lookTarget).sub(s.position).applyQuaternion(s.inverse).divideScalar(s.unit);
    s.up.set(0,1,0).applyQuaternion(world.camera.quaternion).applyQuaternion(s.inverse).normalize();s.fov=world.camera.fov;
    const {sun,fill}=world.lights;
    s.keyPosition.copy(sun.position);s.keyTarget.copy(sun.target.position);s.keyColor.copy(sun.color);s.keyIntensity=sun.intensity;
    s.fillPosition.copy(fill.position);s.fillTarget.copy(fill.target.position);s.fillColor.copy(fill.color);s.fillIntensity=fill.intensity;
    s.key.copy(sun.position).sub(sun.target.position).normalize().applyQuaternion(s.inverse);s.fill.copy(fill.position).sub(fill.target.position).normalize().applyQuaternion(s.inverse);
    if(s.hemi){s.skyColor.copy(s.hemi.color);s.groundColor.copy(s.hemi.groundColor);s.ambient=s.hemi.intensity;}else{s.skyColor.set('#bed8ee');s.groundColor.set('#352a23');s.ambient=.7;}
    s.fog=world.scene.fog;s.density=s.fog?.density??0;if(s.fog)s.fogColor.copy(s.fog.color);else s.fogColor.set('#17232c');
    return s;
  }
  function apply(s,q,fov,keyIntensity,fillIntensity,ambient,fogDensity){
    const w=s.world,camera=w.camera;
    camera.position.copy(common.position).multiplyScalar(s.unit).applyQuaternion(s.rotation).add(s.position);
    w.lookTarget.copy(common.target).multiplyScalar(s.unit).applyQuaternion(s.rotation).add(s.position);
    savedUp.copy(camera.up);camera.up.copy(common.up).applyQuaternion(s.rotation).normalize();camera.fov=fov;camera.lookAt(w.lookTarget);camera.up.copy(savedUp);camera.updateProjectionMatrix();camera.updateMatrixWorld(true);
    const {sun,fill}=w.lights;
    sun.target.position.copy(s.position);sun.position.copy(common.key).applyQuaternion(s.rotation).multiplyScalar(60*s.unit).add(s.position);sun.color.copy(common.keyColor);sun.intensity=keyIntensity;sun.target.updateMatrixWorld();
    fill.target.position.copy(s.position);fill.position.copy(common.fill).applyQuaternion(s.rotation).multiplyScalar(35*s.unit).add(s.position);fill.color.copy(common.fillColor);fill.intensity=fillIntensity;fill.target.updateMatrixWorld();
    if(s.hemi){s.hemi.color.copy(common.skyColor);s.hemi.groundColor.copy(common.groundColor);s.hemi.intensity=ambient;}
    if(s.fog){s.fog.color.copy(common.fogColor);s.fog.density=fogDensity/s.unit;}
  }
  function restore(s){if(!s)return;const {sun,fill}=s.world.lights;sun.position.copy(s.keyPosition);sun.target.position.copy(s.keyTarget);sun.color.copy(s.keyColor);sun.intensity=s.keyIntensity;sun.target.updateMatrixWorld();fill.position.copy(s.fillPosition);fill.target.position.copy(s.fillTarget);fill.color.copy(s.fillColor);fill.intensity=s.fillIntensity;fill.target.updateMatrixWorld();if(s.hemi){s.hemi.color.copy(s.skyColor);s.hemi.groundColor.copy(s.groundColor);s.hemi.intensity=s.ambient;}if(s.fog){s.fog.color.copy(s.fogColor);s.fog.density=s.density;}}
  function project(s,out){for(let i=0;i<8;i++)out[i].copy(corners[i]).applyMatrix4(s.parcel.matrixWorld).project(s.world.camera);}
  function align(worldA,worldB,p,width,height){
    const a=capture(worldA),b=capture(worldB);if(!a||!b){metrics={active:false,reason:'parcel-anchor-unavailable'};return false;}
    activeA=a;activeB=b;
    sphericalA.setFromVector3(a.relative);sphericalB.setFromVector3(b.relative);
    const turn=THREE.MathUtils.euclideanModulo(sphericalB.theta-sphericalA.theta+Math.PI,Math.PI*2)-Math.PI;
    spherical.radius=Math.exp(mix(Math.log(Math.max(.1,sphericalA.radius)),Math.log(Math.max(.1,sphericalB.radius)),p));spherical.theta=sphericalA.theta+turn*p;spherical.phi=mix(sphericalA.phi,sphericalB.phi,p);common.position.setFromSpherical(spherical);
    common.target.lerpVectors(a.target,b.target,p);common.up.lerpVectors(a.up,b.up,p).normalize();if(common.up.lengthSq()<.1)common.up.set(0,1,0);
    common.key.lerpVectors(a.key,b.key,p).normalize();common.fill.lerpVectors(a.fill,b.fill,p).normalize();common.keyColor.copy(a.keyColor).lerp(b.keyColor,p);common.fillColor.copy(a.fillColor).lerp(b.fillColor,p);common.skyColor.copy(a.skyColor).lerp(b.skyColor,p);common.groundColor.copy(a.groundColor).lerp(b.groundColor,p);common.fogColor.copy(a.fogColor).lerp(b.fogColor,p);
    const fov=mix(a.fov,b.fov,p),key=mix(a.keyIntensity,b.keyIntensity,p),fill=mix(a.fillIntensity,b.fillIntensity,p),ambient=mix(a.ambient,b.ambient,p),fog=mix(a.density*a.unit,b.density*b.unit,p);
    apply(a,p,fov,key,fill,ambient,fog);apply(b,p,fov,key,fill,ambient,fog);project(a,cornerA);project(b,cornerB);
    let error=0,minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;
    for(let i=0;i<8;i++){const x=cornerA[i],y=cornerB[i];error=Math.max(error,Math.hypot((x.x-y.x)*width*.5,(x.y-y.y)*height*.5));minX=Math.min(minX,x.x);maxX=Math.max(maxX,x.x);minY=Math.min(minY,x.y);maxY=Math.max(maxY,x.y);}
    anchor.set((minX+maxX)*.25+.5,(minY+maxY)*.25+.5);size.set(Math.max(.025,(maxX-minX)*.25),Math.max(.025,(maxY-minY)*.25));
    metrics={active:true,from:worldA.id,to:worldB.id,progress:p,storyIdA:a.parcel.userData.storyId,storyIdB:b.parcel.userData.storyId,maxCornerErrorPx:error,anchor:anchor.toArray(),halfSize:size.toArray(),relativeDistance:spherical.radius,fov,keyIntensity:key,fogDensityInParcelUnits:fog};
    return true;
  }
  return{align,anchor,size,restore(){restore(activeA);restore(activeB);activeA=activeB=null;},idle(){metrics={active:false};},getState(){return metrics;}};
}
