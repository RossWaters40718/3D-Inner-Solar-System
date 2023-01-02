import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Tk, ttk, font, messagebox, Menu
from tkinter import DoubleVar, StringVar, IntVar, BooleanVar, Toplevel
from win32api import GetMonitorInfo, MonitorFromPoint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import matplotlib.animation as animation
from astropy.time import Time
from astroquery.jplhorizons import Horizons
from astropy.coordinates import get_moon
from astropy.coordinates import solar_system_ephemeris
import astropy.units as u
import numpy as np
import pathlib
import os
import re
def about():
       messagebox.showinfo('ABOUT', 'Creator: Ross Waters\nEmail: RossWatersjr@gmail.com'\
              '\nProgram: Inner Solar System\nRevision: 2.3.6'\
              '\nLast Revision Date: 01/02/2023\nCreated With: Python 3.11.0'\
              '\nCreated For Windows 10/11')
def set_defaults():
    plt.tight_layout()
    root.state('zoomed')
    root.resizable(False, False)
    Anim_Speed.set(1)
    Start_Date.set('2020-01-01T00:00:00')
    Old_StartDate.set(Start_Date.get())
    Duration.set(1.0) # Earth Duration Years
    Old_Duration.set(Duration.get())# Comparison For Change
    Increment.set(24.0) # Hours (Earth Rotational Resolution)
    Old_Increment.set(Increment.get())
    inc=Increment.get()
    moon_orbits.set('')
    step=inc/24
    Index_Passed.set(0)        
    Increment_Step.set(step) # Time Increments
    dur=Duration.get()
    span=int(dur*365.256)/step
    Time_Span.set(span)
    ax.axis(True)
    grid_status.set('on')
def reset():# Reset the axes properties
    plt.cla()
    ax.set_xlim3d([-1.1,1.1])
    ax.set_xlabel('X = AU',ha='center',color='#7b7b7b',fontsize=9,weight='normal',style='italic')
    ax.set_ylim3d([-1.1,1.1])
    ax.set_ylabel('Y = AU', ha='center',color='#7b7b7b',fontsize=9, weight='normal', style='italic')
    ax.set_zlim3d([-1.1,1.1])
    ax.set_zlabel('Z = AU',ha='center',color='#7b7b7b',fontsize=9,weight='normal',style='italic')
    ax.set_box_aspect(aspect=(1,1,1))# Set Aspect Ratio = Equal
    fig.add_axes(ax)        
    g2v.create_sun(0.15)#Draw The Sun
    stat=grid_status.get()# Keep Grid Status Same
    if stat=='off':
        ax.axis(False)
        grid_status.set('off')
        Grid_Text.set('Turn Grid ON') 
    else:
        ax.axis(True)
        grid_status.set('on')
        Grid_Text.set('Turn Grid OFF')
def anim_advance(present_index):# Update Widgets That Are Increment Dependent
    present_index+=1
    present_index=Index_Passed.get()
    inc=Increment_Step.get()
    day=(present_index+1)*inc
    earth_days_past.set(str('Earth Days: '+str(round(day,6)))+' / Orbits: '+str(round((day/365.256),6)))
    mercury_days_past.set(str('Mercury Days: '+str(round(23.9345/1407.6*day,6)))+' / Orbits: '+str(round(day/87.969,6)))
    venus_days_past.set(str('Venus Days: '+str(round(23.9345/5832.5*day,6)))+' / Orbits: '+str(round(day/224.701,6)))
    mars_days_past.set(str('Mars Days: '+str(round(23.9345/24.6229*day,6)))+' / Orbits: '+str(round(day/686.980,6)))
    moon_orbits.set(str('Number Of Moon Orbits (Earth) = '+str(round(day/27.3217,6))))
    if int(Time_Span.get())-(present_index+2)<=0:
        Anim_Active.set(False) # Time Frame Complete
        stop_button['state']="normal"
        top_entries[2]['state']="normal"
        start_button['state']="active"
    return g2v.orbit()
def init():# Prevent First Frame From Being Called Twice.
    return g2v.orbit()
def anim_start(frames, speed):# Start Animation
    global anim
    Anim_Active.set(True)
    anim=animation.FuncAnimation(fig=fig ,init_func=init, func=anim_advance, repeat=False, frames=frames, blit=True, interval=speed, cache_frame_data='False')
def anim_restart():# Resume From Where Stop Cmd
    dur=Duration.get()
    val1=Old_Duration.get()
    date=Start_Date.get()
    val2=Old_StartDate.get()
    inc=Increment.get()
    val3=Old_Increment.get()
    g2v.time = Time(Stopped_Time.get()).jd
    if dur!=val1 or date!=val2 or inc!=val3:# If Any Values Changed (Start Date, Duration, Increment) Then Start Fresh
        Anim_Active.set(False)
        start()
        return
    else: # Resume Where Left Off
        if Anim_Active.get():
            frames=int((Time_Span.get()-Index_Passed.get())-1)
        speed=Anim_Speed.get()
        anim_start(frames,speed)
        return
def start():# Start Animation
    header.set('{Nearest Distances To Earth, Date / UTC Time}')
    top_entries[2]['state']="normal"
    start_button['state']="disabled"
    stop_button['state']="active"
    dur=Duration.get()
    val1=Old_Duration.get()
    date=Start_Date.get()
    val2=Old_StartDate.get()
    inc=Increment.get()
    val3=Old_Increment.get()
    if dur!=val1 or date!=val2 or inc!=val3:
        Old_Duration.set(dur)
        Old_StartDate.set(date)
        Old_Increment.set(inc)
        step=inc/24
        Increment_Step.set(step)
        Anim_Active.set(False)
        Astropy_Moon()
    if int(Time_Span.get()-1)==Index_Passed.get():Anim_Active.set(False)
    active=Anim_Active.get()
    if active: # ON GOING
        anim_restart()
        return
    else:# Start Fresh
        Index_Passed.set(0)
        mercury_days_past.set('')
        venus_days_past.set('')
        earth_days_past.set('')
        mars_days_past.set('')
        mercury_distance.set('')
        venus_distance.set('')
        moon_distance.set('')
        mars_distance.set('')
        mercury_sun.set('')
        venus_sun.set('')
        earth_sun.set('')
        mars_sun.set('')
        mercury_close.set('')        
        venus_close.set('')        
        mars_close.set('')        
        moon_close.set('')
        sun_close.set('')
        Old_Moon.set(1.0e24)
        Old_Mercury.set(1.0e24)
        Old_Venus.set(1.0e24)
        Old_Mars.set(1.0e24)
        Old_Sun.set(1.0e24)
        dur=Duration.get()
        val1=Old_Duration.get()
        if dur<= 0.0: # Duration Years
            msg1='Time Duration Must Be Set To Number > 0 For Animation.\n'
            msg2='Please Enter A Time Duration.'
            messagebox.showwarning('Time Duration', msg1+msg2)
            top_entries[1].focus
            return
        date=Start_Date.get()
        val2=Old_StartDate.get() 
        if date=='': # Start Date
            msg1='A Start Date Must Be Entered For Animation.\n'
            msg2='Example: 2022-01-15'
            messagebox.showwarning('Start Date', msg1+msg2)            
            top_entries[0].focus
            return
        inc=Increment.get()
        val3=Old_Increment.get()
        if inc<= 0.0: # Increment Hrs 
            msg1='Time Increment Must Be Set To Number > 0 For Animation.\n'
            msg2='Please Enter A Time Increment.'
            messagebox.showwarning('Time Increment', msg1+msg2)
            top_entries[1].focus
            return
        else: # Something Changed
            if dur!=val1 or date!=val2 or inc!=val3:
                Old_Duration.set(dur)
                Old_StartDate.set(date)
                Old_Increment.set(inc)
                step=inc/24
                Increment_Step.set(step)
                Astropy_Moon()
            else:
                step=inc/24
                Increment_Step.set(step) # Time Increments
                span=int(round((dur*365.256)/step))
                Time_Span.set(span)
                Horizon_Planets()
                g2v.time=Time(val2).jd
                speed=Anim_Speed.get()
                et=step*3
                display_time=str(Time(Epoch[-1])+et*u.day)
                display_time=display_time.replace('T','  Hrs: ')[:-4] # Trim mSec From End And Add Hrs Label
                End_Time.set(' @ End Date: '+display_time)
                frames=int(len(Epoch))
                plt.cla()
                anim_start(frames, speed)
            return
def on_resize(event):
    if root.state()=='zoomed':
        font_size= 14
        root.font['size'] = font_size
        present_font['size'] = font_size + 3
    return
def grid(event): # Grid Widget
    plt.ion()
    stat=grid_status.get()
    if stat=='off':
        ax.axis(True)
        grid_status.set('on')
        Grid_Text.set('Turn Grid OFF') 
    else:
        ax.axis(False)
        grid_status.set('off')
        Grid_Text.set('Turn Grid ON') 
    plt.ioff()
    return
def mouse_clicked(event): # Entry Widgets
    try:anim.event_source.stop()
    except Exception:
        pass
    top_entries[2]['state']="normal"
    start_button['state']="active"
    stop_button['state']="normal"
    return
def callback(event): # Entry Widgets
    try:anim.event_source.stop()
    except Exception:
        pass
    Anim_Active.set(False)
    start()
    return
def unit_change(event): # AU, Metric, U.S.
    try:anim.event_source.stop()
    except Exception:
        pass
    selected = event.widget.get()
    Units.set(selected)
    status=Anim_Active.get()
    if status: # Change Units And Restart
        # Restart Due To Incorrect Nearest Distance Vlues 
        Anim_Active.set(False)
        start()
    return
def destroy():# X Icon Or Exit Program Clicked
    try:anim.event_source.stop()
    except Exception:
        pass
    Lunar.clear()
    Real_Lunar.clear()
    for widget in root.winfo_children():
        if isinstance(widget, tk.Canvas):widget.destroy()
        else:widget.destroy()
        os._exit(0)
    return
def menu_popup(event):# display the popup menu
    active=Anim_Active.get()
    if not active:
        try:popup.tk_popup(event.x_root, event.y_root)
        finally:popup.grab_release()
def validate_dates(string): # Entry Date Widget
    #Date Widget Allowed Integers and -
    regex=re.compile(r'[(0-9-)]*$') # Allow
    result=regex.match(string)
    return (string == "" 
    # Prevent duplicates
    or (string.count(string)>0
        and result is not None
        and result.group(0) != ""))       
def on_validate_dates(P):return validate_dates(P)
def validate_double(dbl_value): # Duration, Increment Widgets
    str_value=str(dbl_value)
    # Allowed Integers Only
    regex=re.compile(r'[(0-9.)]*$') # Allow
    result=regex.match(str_value)
    return (str_value == "" 
    # Prevent duplicates
    or (str_value.count(str_value)>0
        and result is not None
        and result.group(0) != ""))       
def on_validate_double(P):return validate_double(P)
class Bodies: # Define Planets
    def __init__(self,name,rad,cmp,xyz,v_xyz):
        if name ==301:self.name=5 # Change 301 To 5 For Iteration
        else:self.name=name   
        self.rad=np.double(rad)
        self.cmp=cmp
        self.xyz=np.array(xyz, dtype=float)
        x,y,z=self.xyz[0:3]
        self.v_xyz=np.array(v_xyz, dtype=float)
        u=np.linspace(0,2*np.pi,100) # Create 100 Element np Array (0 - 2*pi)
        v=np.linspace(0,np.pi,100)
        x=np.double(self.rad)*np.outer(np.cos(u),np.sin(v))+np.double(x) 
        y=np.double(self.rad)*np.outer(np.sin(u),np.sin(v))+np.double(y)
        z=np.double(self.rad)*np.outer(np.ones(np.size(u)),np.cos(v))+np.double(z)
        self.plot=ax.plot_surface(x,y,z,rstride=6,cstride=6,cmap=self.cmp,linewidth=0,alpha=1)
class G2V_Solar_System:
    def __init__(self):
        self.planets=[]
        self.Planets_Data=[]
    def add_planet(self,planet):
        self.planets.append(planet)
    def planet_properties(self,radius,cmap):
        self.radius=radius
        self.colormap=cmap
        u=np.linspace(0,2*np.pi, 100)
        v=np.linspace(0,np.pi,100)
        self.x=np.outer(np.cos(u),np.sin(v))
        self.y=np.outer(np.sin(u),np.sin(v))
        self.z=np.outer(np.ones(np.size(u)),np.cos(v))
        top_cm=['binary_r','copper','GnBu','Reds','Pastel1']
        btm_cm=['binary','copper_r','BuGn_r','Reds_r','Pastel1']
        radius=[0.0383,0.0949,0.1,0.0532,0.02724]
        for i, p in enumerate(radius):
            top=cm.get_cmap(top_cm[i],128) # r means reversed version
            bottom=cm.get_cmap(btm_cm[i],128)# combine it all
            newcolors=np.vstack((top(np.linspace(0,1,128)),bottom(np.linspace(0,1,128))))
            self.colormap.append(ListedColormap(newcolors))
            self.radius.append(p)
    def create_sun(self,rad):
        N=256
        color1=np.ones((N,4))# Create Red Colormaps (Top)
        color1[:,0]=np.linspace(255/256,1,N) # R = 255
        color1[:,1]=np.linspace(100/256,1,N) # G = 232
        color1[:,2]=np.linspace(65/256,1,N)  # B = 11
        color1_cmp = ListedColormap(color1)
        color2=np.ones((N,4))# Create Red Colormaps (Bottom)
        color2[:,0]=np.linspace(255/256,1,N)
        color2[:,1]=np.linspace(100/256,1,N)
        color2[:,2]=np.linspace(65/256,1,N)
        color2_cmp = ListedColormap(color2)
        new_cmap = np.vstack((color1_cmp(np.linspace(0, 1, 128)),color2_cmp(np.linspace(1, 0, 128))))
        cmap=ListedColormap(new_cmap)#Combine Top And Bottom Colormaps
        u=np.linspace(0,2*np.pi,100)
        v=np.linspace(0,np.pi,100)
        x=np.double(rad)*np.outer(np.cos(u),np.sin(v))
        y=np.double(rad)*np.outer(np.sin(u),np.sin(v))
        z=np.double(rad)*np.outer(np.ones(np.size(u)),np.cos(v))
        self.plot=ax.plot_surface(x,y,z,rstride=6,cstride=6,cmap=cmap,linewidth=0,alpha=1)
    def finalize_planet_data(self): # Finalize All Planet Data, Place In Dict 
        dt=Increment_Step.get()
        mercury,venus,earth,mars,moon={},{},{},{},{}
        temp,temp2=[],[]
        for p in self.planets:
            for e in range(0,len(Epoch)):
                if p.name!=5: # Moon Data Already Present
                    p.xyz+=p.v_xyz*dt
                    acc=-2.959e-4*p.xyz/np.sum(p.xyz**2)**(3./2)
                    p.v_xyz+=acc*dt
                    temp=p.xyz.tolist()
                    if p.name==1:mercury[e]=[element for element in temp]
                    elif p.name==2:venus[e]=[element for element in temp]
                    elif p.name==3: # Create And Combine Earth Data To Moon Data
                        earth[e]=[element for element in temp]
                        combined=zip(earth[e],Lunar[e]) # Earth + Moon
                        temp2=[x+y for (x,y) in combined]
                        moon[e]=[element for element in temp2]
                    elif p.name==4:mars[e]=[element for element in temp]
                    temp=[]
                    temp2=[]
        self.Planets_Data=[mercury,venus,earth,mars,moon] 
    def orbit(self):
        index=Index_Passed.get()
        if index==0:reset()
        meas=Units.get()
        dt=Increment_Step.get()
        self.time+=dt
        plots=[]
        for i, p in enumerate(self.planets):
            p.plot.remove()
            if index>=len(Epoch): # Prevent Index Out Of Bounds Error
                last_key=self.Planets_Data[i][index-1]
                self.Planets_Data[i][index]=last_key
                if p.name==5:# Moon
                    last_key=Real_Lunar[index-1]
                    Real_Lunar[index]=last_key
            p.xyz=self.Planets_Data[i][index]    
            x,y,z=np.double(p.rad)*self.x+np.double(p.xyz[0]),np.double(p.rad)*self.y+np.double(p.xyz[1]),np.double(p.rad)*self.z+np.double(p.xyz[2]) 
            p.plot=ax.plot_surface(x,y,z,rstride=6,cstride=6,cmap=p.cmp,linewidth=1,alpha=1)
        display_time=Time(self.time,format='jd').iso 
        Stopped_Time.set(Time(self.time, format='jd').iso )
        display_time=display_time.replace(' ','  Hrs: ')[:-4]
        Present_Time.set('Present Date: '+display_time)
        if p.name==5: # Update All Display Widgets
            d1=str(round(np.sqrt((Real_Lunar[index][0])**2+(Real_Lunar[index][1])**2+(Real_Lunar[index][2])**2),18))
            new_moon=float(d1)
            d2=str(round(np.sqrt((self.Planets_Data[2][index][0])**2+(self.Planets_Data[2][index][1])**2+
                (self.Planets_Data[2][index][2])**2),18))
            new_sun=float(d2)
            d3=str(round(np.sqrt((self.Planets_Data[0][index][0]-self.Planets_Data[2][index][0])**2+
                (self.Planets_Data[0][index][1]-self.Planets_Data[2][index][1])**2+(self.Planets_Data[0][index][2]-
                    self.Planets_Data[2][index][2])**2),18))
            new_mercury=float(d3)
            d4=str(round(np.sqrt((self.Planets_Data[0][index][0])**2+(self.Planets_Data[0][index][1])**2+
                (self.Planets_Data[0][index][2])**2),18))
            d5=str(round(np.sqrt((self.Planets_Data[1][index][0]-self.Planets_Data[2][index][0])**2+
                (self.Planets_Data[1][index][1]-self.Planets_Data[2][index][1])**2+(self.Planets_Data[1][index][2]-
                    self.Planets_Data[2][index][2])**2),18))
            new_venus=float(d5)
            d6=str(round(np.sqrt((self.Planets_Data[1][index][0])**2+(self.Planets_Data[1][index][1])**2+
                (self.Planets_Data[1][index][2])**2),18))
            d7=str(round(np.sqrt((self.Planets_Data[3][index][0]-self.Planets_Data[2][index][0])**2+
                (self.Planets_Data[3][index][1]-self.Planets_Data[2][index][1])**2+(self.Planets_Data[3][index][2]-
                    self.Planets_Data[2][index][2])**2),18))
            new_mars=float(d7)
            d8=str(round(np.sqrt((self.Planets_Data[3][index][0])**2+(self.Planets_Data[3][index][1])**2+
                (self.Planets_Data[3][index][2])**2),18))
            if meas=='AU': # Leave As Is
                unit=' au'
            elif meas=='U.S.': # Convert AU To Miles
                d1=str(round(float(d1)*92955807.26743,18))
                new_moon=float(d1)
                d2=str(round(float(d2)*92955807.26743,18))
                new_sun=float(d2)
                d3=str(round(float(d3)*92955807.26743,18)) 
                new_mercury=float(d3)
                d4=str(round(float(d4)*92955807.26743,18)) 
                d5=str(round(float(d5)*92955807.26743,18))
                new_venus=float(d5)
                d6=str(round(float(d6)*92955807.26743,18))
                d7=str(round(float(d7)*92955807.26743,18)) 
                new_mars=float(d7)
                d8=str(round(float(d8)*92955807.26743,18)) 
                unit=' mi'
            elif meas=='Metric': # Convert AU To Kilometers
                d1=str(round(float(d1)*149597870.691,18)) 
                new_moon=float(d1)
                d2=str(round(float(d2)*149597870.691,18))
                new_sun=float(d2)
                d3=str(round(float(d3)*149597870.691,18))
                new_mercury=float(d3)
                d4=str(round(float(d4)*149597870.691,18)) 
                d5=str(round(float(d5)*149597870.691,18)) 
                new_venus=float(d5)
                d6=str(round(float(d6)*149597870.691,18))
                d7=str(round(float(d7)*149597870.691,18)) 
                new_mars=float(d7)
                d8=str(round(float(d8)*149597870.691,18)) 
                unit=' km'
            moon_distance.set('Distance'+chr(8853)+' To Moon: '+d1+unit)
            earth_sun.set('Distance'+chr(8853)+' To Sun: '+d2+unit)
            mercury_distance.set('Distance'+chr(8853)+' To Earth: '+d3+unit)
            mercury_sun.set('Distance'+chr(8853)+' To Sun: '+d4+unit)
            venus_distance.set('Distance'+chr(8853)+' To Earth: '+d5+unit)
            venus_sun.set('Distance'+chr(8853)+' To Sun: '+d6+unit)
            mars_distance.set('Distance'+chr(8853)+' To Earth: '+d7+unit)
            mars_sun.set('Distance'+chr(8853)+' To Sun: '+d8+unit)
            tol=str(round(dt*24,3))+' hrs'
            if new_sun<Old_Sun.get():
                Old_Sun.set(new_sun)
                sun_close.set('Sun = '+str(d2)+unit)
                sun_time.set('Date: '+display_time+' '+chr(177)+' '+tol)
            if new_moon<Old_Moon.get():
                Old_Moon.set(new_moon)
                moon_close.set('Moon = '+str(d1)+unit)
                moon_time.set('Date: '+display_time+' '+chr(177)+' '+tol)
            if new_mercury<Old_Mercury.get():
                Old_Mercury.set(new_mercury)
                mercury_close.set('Mercury = '+str(d3)+unit)
                mercury_time.set('Date: '+display_time+' '+chr(177)+' '+tol)
            if new_venus<Old_Venus.get():
                Old_Venus.set(new_venus)
                venus_close.set('Venus = '+str(d5)+unit)
                venus_time.set('Date: '+display_time+' '+chr(177)+' '+tol)
            if new_mars<Old_Mars.get():
                Old_Mars.set(new_mars)
                mars_close.set('Mars = '+str(d7)+unit)
                mars_time.set('Date: '+display_time+' '+chr(177)+' '+tol)
        index=Index_Passed.get()
        Index_Passed.set(index+1)
        return plots
class Horizon_Planets():# Initialize All Bodies Including Sun And Moon
    def __init__(self):
        global g2v
        g2v=G2V_Solar_System()
        g2v.time = Time(Start_Date.get()).jd
        radius,color_map=[],[]
        g2v.planet_properties(radius,color_map)
        solar_system_ephemeris.set('builtin')
        for p, planets in enumerate([1, 2, 3, 4, 301]): # 1st, 2nd, 3rd, Moon, 4th planet in solar system
            obj=Horizons(id=planets, location="@sun", epochs=g2v.time, id_type=None).vectors()
            g2v.add_planet(Bodies(planets, radius[p], color_map[p],
                [np.double(obj[xyz]) for xyz in ['x', 'y', 'z']], 
                [np.double(obj[v_xyz]) for v_xyz in ['vx', 'vy', 'vz']]))
        g2v.finalize_planet_data()        
class Astropy_Moon():# Retrieve Moon Data In (AU) For A Given Earth Cycle
    def __init__(self):
        top_entries[2]['state']="disabled"
        quit['state']="disabled"
        start_button['state']="disabled"
        stop_button['state']="disabled"
        start=Start_Date.get()
        if start=='':return
        dur=Duration.get()
        if Duration.get()<=0: return
        step=Increment_Step.get()
        if Increment_Step.get()<=0:return
        incre=Increment.get()
        if Increment.get()<=0:return
        try:
            span=int(round((dur*365.256)/step))
            Time_Span.set(span)
            Increment_Step.set(incre/24)
            global Epoch
            Epoch=Time(start) + np.arange(span)*u.hour*Increment.get()
        except Exception:
            msg1='Something is not correct with Entered Text.\n'
            msg2='Please check the values and try again.'
            messagebox.showwarning('Start Date', msg1+msg2)
            return
        pb = Progressbar(root, orient='horizontal', length=100, mode='determinate')
        pb.place(relx=0.2833333, rely=0.0777777, relwidth=0.4555555, relheight=0.0244444)
        txt1 = tk.Label(root, text = '0%', bg = '#000000', fg ='#ffffff', font=root.font)
        txt1.place(relx=0.7388888, rely=0.0777777, relwidth=0.0666666, relheight=0.0244444)
        txt2 = tk.Label(root, text = 'Please Wait! Retrieving Planetary Data For New Time Duration.', bg = '#000000', fg ='#ffffff', font=root.font)
        txt2.place(relx=0.2833333, rely=0.09555555, relwidth=0.4555555, relheight=0.0244444)
        solar_system_ephemeris.set('builtin')
        for e in range(0,len(Epoch)):  
            moon=get_moon(Epoch[e])
            #For 3D 
            Real_Lunar[e]=[np.double(moon.cartesian.xyz[0]), np.double(moon.cartesian.xyz[1]), np.double(moon.cartesian.xyz[2])]
            #For 2D Plot
            Lunar[e]=[np.double(moon.cartesian.xyz[0]), np.double(moon.cartesian.xyz[1]), np.double(moon.cartesian.xyz[2])]
            Lunar[e]=[element * 60 for element in Lunar[e]] # Exaggerate Moons Orbit To Accomidate Size Of Earth
            root.update_idletasks()
            pb['value']+=100/span
            txt1['text']=round(pb['value'],1),'%'
        pb.destroy()
        txt1.destroy()
        txt2.destroy()
        stop_button['state']="normal"
        top_entries[2]['state']="normal"
        quit['state']="normal"
        start_button['state']="active"
if __name__ == "__main__":
    root=Tk()
    root.wm_title("3D Inner Solar System")
    dir=pathlib.Path(__file__).parent.absolute()
    filename='3DSpace.ico'
    path=os.path.join(dir, filename)
    root.iconbitmap(path)
    root.font=font.Font(family='lucidas', size=10, weight='normal', slant='italic')
    present_font=font.Font(family='lucidas', size=12, weight='normal', slant='italic')
    default_fontsize = 10
    monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
    work_area = monitor_info.get("Work")
    monitor_area = monitor_info.get("Monitor")
    screen_width=work_area[2]
    screen_height=work_area[3]
    taskbar_hgt=(monitor_area[3]-work_area[3])
    root_hgt = screen_height-taskbar_hgt
    root_wid = root_hgt 
    default_hgt = root_hgt
    x=(screen_width/2)-(root_wid/2)
    y=(screen_height/2)-(root_hgt/2)
    root.geometry('%dx%d+%d+%d' % (root_wid, root_hgt, x, 0, ))
    root.configure(bg='#000000')
    root.bind("<Configure>", on_resize)
    root.option_add('*TCombobox*Listbox.font', root.font)
    root.protocol("WM_DELETE_WINDOW", destroy)
    root.bind("<Button-3>", menu_popup)
    px=1/plt.rcParams['figure.dpi']
    fig = plt.figure(figsize=(root_hgt*px,root_wid*px),facecolor='#000000',dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    ax = fig.add_subplot(111, projection="3d")
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas = Toplevel
    ax.set_facecolor('#000000')
    ax.xaxis.pane.set_color('#000000')
    ax.xaxis.pane.fill=True
    ax.yaxis.pane.set_color('#000000')
    ax.yaxis.pane.fill=True
    ax.zaxis.pane.set_color('#000000')
    ax.zaxis.pane.fill=True
    ax.tick_params(axis='x',colors='#7b7b7b')
    ax.tick_params(axis='y',colors='#7b7b7b')
    ax.tick_params(axis='z',colors='#7b7b7b')
    ax.xaxis._axinfo["grid"].update({"linewidth":0.5})
    ax.yaxis._axinfo["grid"].update({"linewidth":0.5})
    ax.zaxis._axinfo["grid"].update({"linewidth":0.5})
    ax.xaxis._axinfo["grid"].update({"color":('#7b7b7b')})
    ax.yaxis._axinfo["grid"].update({"color":('#7b7b7b')})
    ax.zaxis._axinfo["grid"].update({"color":('#7b7b7b')})
    ax.view_init(azim=-45, elev=25)
    plt.tight_layout()
    # Variables
    Lunar={}
    Real_Lunar={}
    Index_Passed=IntVar()
    Index_Passed.set(-1)   
    Stopped_Time=StringVar()
    Stopped_Time.set('')
    Anim_Active=BooleanVar()
    Anim_Active.set(False)
    Anim_Speed=IntVar()
    Anim_Speed.set(1)
    Old_Sun=DoubleVar()
    Old_Moon=DoubleVar()
    Old_Mercury=DoubleVar()
    Old_Venus=DoubleVar()
    Old_Mars=DoubleVar()
    Start_Date=StringVar() # Start Date
    Old_StartDate = StringVar()
    Time_Span = DoubleVar()
    Duration=DoubleVar() # Earth Time Duration
    Old_Duration=DoubleVar()
    Increment = DoubleVar()# Time Increment Entry
    Old_Increment=DoubleVar()
    Increment_Step=DoubleVar()
    Units = tk.StringVar() # Units Of Measurement
    grid_status = StringVar() # Grid On/Off Button
    grid_status.set('on')
    Grid_Text=StringVar()
    Present_Time=StringVar() # Present Date Label
    End_Time=StringVar()
    earth_days_past=StringVar()
    moon_distance=StringVar()
    moon_orbits=StringVar()
    earth_sun=StringVar()
    mercury_days_past=StringVar()
    mercury_distance=StringVar()
    mercury_sun=StringVar()
    venus_days_past=StringVar()
    venus_distance=StringVar()
    venus_sun=StringVar()
    mars_days_past=StringVar()
    mars_distance=StringVar()
    mars_sun=StringVar()
    header=StringVar()
    sun_close=StringVar()
    sun_time=StringVar()
    moon_close=StringVar()
    moon_time=StringVar()
    mercury_close=StringVar()
    mercury_time=StringVar()
    venus_close=StringVar()
    venus_time=StringVar()
    mars_close=StringVar()
    mars_time=StringVar()
    top_lbls=[]
    x_rel=[0.155,0.275,0.385,0.50]
    wid=[0.11,0.1,0.105,0.05]
    txt=['Start Date / UTC Time','Earth Duration (Yrs.)','Time Increment (Hrs.)','Units']
    for index, element in enumerate(x_rel): # Labels For Top Row Entries
        top_lbls.append([index])
        top_lbls[index]=tk.Label(root, bg='#000000', fg='#ffffff', font=root.font, 
            text=txt[index], justify='left', anchor='c')
        top_lbls[index].place(relx=element, rely=0.005, relwidth=wid[index], relheight=0.0344)
    top_entries=[]
    validates=[validate_dates,validate_double,validate_double]
    cmds=[on_validate_dates,on_validate_double,on_validate_double]
    txt_var=[Start_Date,Duration,Increment]
    for index, element in enumerate(txt_var): # Top Row Entries
        top_entries.append([index])
        top_entries[index]=tk.Entry(root, bg='#000000', fg='#a7f8f8', textvariable=element, font=root.font, 
                justify='center',insertbackground='#ffffff')
        top_entries[index].place(relx=x_rel[index], rely=0.0366666, relwidth=wid[index], relheight=0.0344)
        top_entries[index]['validatecommand']=(top_entries[index].register(validates[index]),'%P','%d')
        cmd=(top_entries[index].register(cmds[index]), '%P')
        top_entries[index].config(validate="key", validatecommand=cmd)
        top_entries[index].config(cursor="xterm #ffffff")
        top_entries[index].bind("<Button-1>", mouse_clicked)
        top_entries[index].bind('<Return>', callback)
    start_button=tk.Button(root, text='Start', background="#000000", foreground='#ffffff', font=root.font, command=lambda: start())
    start_button.place(relx=0.56, rely=0.0366666, relwidth=0.05, relheight=0.0344)
    start_button['state']="active"
    stop_button=tk.Button(root, text='Stop', background="#000000", foreground='#ffffff', font=root.font)
    stop_button.place(relx=0.62, rely=0.0366666, relwidth=0.05, relheight=0.0344)
    stop_button.bind("<Button-1>", mouse_clicked)
    Units=tk.StringVar()
    units_cb=ttk.Combobox(root, textvariable=Units, font=root.font, justify='center')
    units_cb.place(relx=0.5, rely=0.0366666, relwidth=0.05, relheight=0.0344) # using place method
    units_cb['values']=('AU','U.S.','Metric')
    units_cb['state']='readonly'
    units_cb.current(0)
    units_cb.bind("<Button-1>", mouse_clicked)
    units_cb.bind('<<ComboboxSelected>>', unit_change)
    Grid_Text.set('Turn Grid OFF') 
    grid_button=tk.Button(root, textvariable=Grid_Text, background="#000000", foreground='#ffffff', font=root.font,)
    grid_button.place(relx=0.68, rely=0.0366666, relwidth=0.08, relheight=0.0344)
    grid_button.bind("<Button-1>", grid)
   # Quit Button
    quit = tk.Button(root, text='Exit Program', background="#000000", foreground = '#ffffff', font=root.font, command=lambda: destroy())
    quit.place(relx=0.77, rely=0.0366666, relwidth=0.08, relheight=0.0344)
    present_lbl=tk.Label(root, bg='#444444', fg='#a7f8f8', font=present_font, 
        text='', textvariable=Present_Time, justify='left', anchor='w', borderwidth=2, relief="sunken")
    present_lbl.place(relx=0.02, rely=0.15, relwidth=0.235, relheight=0.03)
    y=0.19
    end_lbl=tk.Label(root, bg='#444444', fg='#a7f8f8', font=present_font, 
        text='', textvariable=End_Time, justify='left', anchor='w', borderwidth=2, relief="sunken")
    end_lbl.place(relx=0.02, rely=y, relwidth=0.235, relheight=0.03)
    strvar=[earth_days_past,moon_distance,moon_orbits,earth_sun,mercury_days_past,mercury_distance,
        mercury_sun,venus_days_past,venus_distance,venus_sun,mars_days_past,mars_distance,mars_sun]
    color=['#3292ea','#3292ea','#3292ea','#3292ea','#d2d2d2','#d2d2d2','#d2d2d2','#cd9f6d','#cd9f6d',
        '#cd9f6d','#cc0000','#cc0000','#cc0000']
    do_lbl=[] # Days Past Data / Orbits Data
    y+=0.04   
    for index, element in enumerate(strvar):
        do_lbl.append([index])
        do_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text='', textvariable=element, justify='left', anchor='w')
        do_lbl[index].place(relx=0.02, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    y+=0.025
    nd_lbl=[] # Nearest Distance / Date/Time Data
    strvar=[header,sun_close,sun_time,moon_close,moon_time,mercury_close,mercury_time,venus_close,venus_time,mars_close,mars_time]
    color=['#a7f8f8','#ff7469','#ff7469','#ffffff','#ffffff','#999999','#999999','#cd9f6d',
        '#cd9f6d','#cc0000','#cc0000']
    for index, element in enumerate(strvar):
        nd_lbl.append([index])
        nd_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        textvariable=element, justify='left', anchor='w')
        nd_lbl[index].place(relx=0.02, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    y=0.11
    bd_lbl=[] # Body Diameters
    text=['{Body Diameters}','Sun = 1,391,983 km, 864,938 mi','Earth = 12,741.98 km, 7,917.5 mi',
        'Moon = 3,474.735 km, 2,159.1 mi','Mercury = 4,879.37 km, 3,031.9 mi',
        'Venus = 12,103.554 km, 7,520.8 mi','Mars = 6,779.04 km, 4,213.3 mi']
    color=['#a7f8f8','#ff7469','#3292ea','#f3f6f4','#999999','#cd9f6d','#cc0000']
    for index, element in enumerate(text):
        bd_lbl.append([index])
        bd_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        bd_lbl[index].place(relx=0.8, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    bm_lbl=[] # Body Mass
    text=['{Body Masses}','Sun = 1.98847 x 10'+ chr(179) + chr(8304) + ' kg','Earth = 5.97219 x 10'+ chr(178) + chr(8308) + ' kg',
        'Moon = 7.34767 x 10'+ chr(178) + chr(178) + ' kg','Mercury = 3.30104 x 10'+ chr(178) + chr(179) + ' kg',
        'Venus = 4.86732 x 10'+ chr(178) + chr(8308) + ' kg','Mars = 6.4169 x 10'+ chr(178) + chr(179) + ' kg']
    for index, element in enumerate(text):
        bm_lbl.append([index])
        bm_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        bm_lbl[index].place(relx=0.8, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    rp_lbl=[] # Rotation Periods
    color=['#a7f8f8','#3292ea','#f3f6f4','#999999','#cd9f6d','#cc0000']
    text=['{Rotational Periods}','Earth = 23.9345 hrs.','Moon = 655.7 hrs.',
        'Mercury = 1407.6 hrs.','Venus = -5832.5 hrs.','Mars = 24.6229 hrs.']
    for index, element in enumerate(text):
        rp_lbl.append([index])
        rp_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        rp_lbl[index].place(relx=0.8, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    op_lbl=[] # Orbital Periods
    text=['{Orbital Periods}','Earth = 365.256 days','Moon (Earth) = 27.3217 days',
        'Mercury = 87.969 days','Venus = 224.701 days','Mars = 686.980 days']
    for index, element in enumerate(text):
        op_lbl.append([index])
        op_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        op_lbl[index].place(relx=0.8, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    ov_lbl=[] # Orbital Velocities
    text=['{Orbital Velocities}','Earth = 29.8 km/sec, 18.5 mi/sec','Moon = 1.022 km/sec, 0.6350 mi/sec ',
        'Mercury = 47.4 km/sec, 29.4 mi/sec','Venus = 35.0 km/sec, 21.8 mi/sec','Mars = 21.4 km/sec, 15.0 mi/sec']
    for index, element in enumerate(text):
        ov_lbl.append([index])
        ov_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        ov_lbl[index].place(relx=0.8, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    strvar.clear()
    color.clear()
    text.clear()    
    popup=Menu(root, tearoff=0) # PopUp Menu
    popup.add_command(label="About", background='aqua', command=lambda:about())
    set_defaults()
    Astropy_Moon() # Retrieve Moon Data For Time Frame
root.mainloop()