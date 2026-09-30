#!/usr/bin/env python3
"""Large-signal EF86 validation for SMX-3 V2.

Uses the provisional EF86 model in the selected Philips 250 V circuit.
Cathode and screen are treated as AC-bypassed, matching the documented
application circuit intent. The 330 kOhm following-grid load is included.

This test checks the exact manufacturer large-signal anchor:
Vo ~= 50 Vrms at total distortion ~= 5%.

Standard library only.
"""

import math

P={"MU":40.4643134,"EX":1.10072133,"KG1":805.463266,"KG2":2542.71827,"KP":220.481328,"KVB":8.11723096}
VB=250.0
RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0


def l1p(x):
    if x>50:return x
    if x<-50:return math.exp(x)
    return math.log1p(math.exp(x))


def currents(vp,vg2,vg1):
    if vg2<=1e-12 or vp<=0.0:return 0.0,0.0
    z=P["KP"]*(1.0/P["MU"]+vg1/vg2)
    e=(vg2/P["KP"])*l1p(z)
    ia=max(e,0.0)**P["EX"]/P["KG1"]*math.atan(vp/P["KVB"])
    ig2=max(vg2/P["MU"]+vg1,0.0)**P["EX"]/P["KG2"]
    return ia,ig2


def solve_dc():
    vp=80.0; vs=120.0; vk=2.0
    for _ in range(40000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)
        a=VB-ia*RA
        s=VB-ig2*RG2
        k=(ia+ig2)*RK
        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-12:
            return vp,vs,vk,ia,ig2
        d=0.1
        vp=(1-d)*vp+d*a; vs=(1-d)*vs+d*s; vk=(1-d)*vk+d*k
    raise RuntimeError("DC solve failed")


DC=solve_dc()


def solve_plate(vin):
    vp0,vs,vk,ia0,_=DC
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp0+ia0*rload
    vp=vp0
    for _ in range(20000):
        ia,_=currents(vp-vk,vs-vk,vin-vk)
        target=vth-ia*rload
        if abs(target-vp)<1e-12:return vp
        vp=0.8*vp+0.2*target
    raise RuntimeError("plate solve failed")


def measure(vin_rms,n=4096):
    ys=[]
    for i in range(n):
        ph=2.0*math.pi*i/n
        ys.append(solve_plate(vin_rms*math.sqrt(2.0)*math.sin(ph)))
    mean=sum(ys)/n
    ys=[y-mean for y in ys]
    out_rms=math.sqrt(sum(y*y for y in ys)/n)

    amps=[]
    for h in range(1,11):
        re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2.0*math.hypot(re,im)/n)
    thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return out_rms,thd


def find_for_thd(target=5.0):
    lo=0.0; hi=0.6
    for _ in range(60):
        mid=(lo+hi)*0.5
        _,d=measure(mid,2048)
        if d<target:lo=mid
        else:hi=mid
    vi=(lo+hi)*0.5
    vo,d=measure(vi,4096)
    return vi,vo,d


def main():
    vi,vo,d=find_for_thd(5.0)
    print("SMX-3 V2 EF86 large-signal validation")
    print(f"DC plate node = {DC[0]:.9f} V")
    print(f"DC screen node = {DC[1]:.9f} V")
    print(f"DC cathode = {DC[2]:.9f} V")
    print(f"input for 5% THD = {vi:.9f} Vrms")
    print(f"output at 5% THD = {vo:.9f} Vrms")
    print(f"THD = {d:.9f} %")
    print("Philips target output at 5% THD = 50 Vrms")
    error=100.0*(vo-50.0)/50.0
    print(f"output error = {error:+.6f}%")

    if abs(error)>10.0:
        raise SystemExit("FAIL: provisional EF86 model misses the Philips large-signal anchor")

    print("PASS: EF86 large-signal anchor within provisional tolerance")


if __name__=="__main__":
    main()
