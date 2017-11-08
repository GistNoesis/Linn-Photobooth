include <Getriebe.scad>



module attachpulleyholes(h)
{
    union()
{
    rotate([0,0,45])
    for (deg = [0:90:(360-1)] )
    {
        rotate( [0,0,deg])
        translate([20,0,0])
        cylinder( r=2,h=2*h,center=true,$fn=200);
    }
    
}

    
    
}

radius608=11.0;

module gear(h,nbteeth,flip,angle)
{

difference()
    {
rotate([flip,0,0])
translate([0,0,-h/2])
stirnrad(2, nbteeth, h, 2*radius608, 20, angle);

union()
        {
    //    translate([20,0,0])
    // cylinder( r=5, h=20,center=true);      
attachpulleyholes(h);
        }

    }

}




module piniongear(h,nbteeth,r=3)
{
 fixh = 5;
union()
{
rotate( [0,180,0])
translate([0,0,-h/2-0.01])
stirnrad(2, nbteeth, h, 5, 20, -30);
    
translate([0,0,h/2-0.01])
stirnrad(2, nbteeth, h, 5, 20, 30);
translate([0,0,h+7/2])
difference()
{
union()
{
translate([0,0,fixh/2-0.02])
cylinder( r = 4, h=fixh, center= true);
translate( [3,0,fixh/2-0.02] )
    cube( [6,3,fixh],center=true);
}
union()
{
translate([0,0,fixh/2])
cylinder( r = r,h=fixh+ 0.01,center=true);
translate( [3,0,fixh/2] )
    cube( [6.01,1,fixh+0.01],center=true);

translate([4.5,0,fixh/2])
rotate( [90,0,0])
cylinder( r= 1.0, h = 100, center=true);
}
}
}
}



module drivepulley( rin,rout,h)
{



difference()
{
difference()
{
union()
{
difference()
{
union()
    {
        translate([0,0,h/4])
        cylinder( r1 = rout,r2=rin, h=h/2,center=true,$fn=200);
        translate([0,0,-h/4])
        cylinder( r1 = rin,r2=rout, h=h/2,center=true,$fn=200);
        
    }
cylinder( r= 16,h=10,$fn=200);
}

cylinder( r=14,h=h,center=true,$fn=200);
}
union()
{
attachpulleyholes( h );
cylinder( r=radius608,h=2*h,center=true,$fn=200);
}

union()
{
rotate([90,0,180] )
cylinder( r =1.5,h=100,center=false,$fn=200);

translate([0,14,0])
cylinder( r =3.0,h=10,center=false,$fn=200);
}

}



}
}



module attach2020holes( e = 3)
{
    translate([0,-43,0] )
    cylinder(r=2.5,h=10*e,center=true,$fn=200);

translate([0,-58,0] )
    cylinder(r=2.5,h=10*e,center=true,$fn=200);

translate([0,-73,0] )
    cylinder(r=2.5,h=10*e,center=true,$fn=200);
}

module support( e =3)
{
difference()
{
translate( [0,-35,10])
cube( [20,90,e],center=true);
union()
{
cylinder(r=4,h=10*e,center=true,$fn=200);
attach2020holes(e);

}


}
    
    
}



module spacer( h = 3, r = 4.2)
{
    difference()
    {
    cylinder( r = r +1.5,h=h,center=true,$fn=200);
    cylinder( r = r ,h=2*h,center=true,$fn=200);
    }
}




module pouliemount( e = 4, l =60 )
{
    
    union()
    {
    difference()
    {
      cylinder( r =28, h = e, center=true, $fn=200);
      union()
        {
      cylinder( r =8, h = 2*e, center=true, $fn=200);
            attachpulleyholes(e);
            rotate([0,0,45])
            union()
            {
            for (deg = [0:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,e-4.9])
                cylinder( r1=2,r2=4.0,h=3,center=false,$fn=200);
            }
            for (deg = [90:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,0])
                cylinder( r=4.5,h=2*e,center=true,$fn=6);
            }
            }
            
        }
    }
        difference()
    {
        translate( [0,-20 - l/2 ,0])
        cube( [20,l,e] ,center=true);
        attach2020holes(e);
    }
    
    }   
}
    
module pouliemountspacer( e = 3 )
{
    union()
    {
    difference()
    {
      cylinder( r =28, h = e, center=true, $fn=200);
      union()
        {
      cylinder( r =8, h = 2*e, center=true, $fn=200);
            attachpulleyholes(e);
            rotate([0,0,45])
            union()
            {
            for (deg = [0:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,e-3.0 - e/2+0.01])
                cylinder( r1=2,r2=4.0,h=3,center=false,$fn=200);
            }
            for (deg = [90:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,0])
                cylinder( r=4.5,h=2*e,center=true,$fn=6);
            }
            }
            
        }
    }
    
    
    }   
    
    
}


    


module roll( e = 4 )
{
    difference()
    {
    cube( [20+e,20,50] ,center = true);
    union()
        {
        translate( [0,0,-e] )
        cube( [15+e,30,50] ,center = true);
         cylinder( r=4, h =100*e, center = true,$fn=200);
         
         translate( [0,0,-5] )
            {
         rotate([0,90,0])
         cylinder( r=2.5, h =40,center=true,$fn=200);
         translate( [0,0,-15] )
         rotate([0,90,0])
         cylinder( r=2.5, h =40,center=true,$fn=200);
         translate( [0,0,15] )
         rotate([0,90,0])
         cylinder( r=2.5, h =40,center=true,$fn=200);
            }
        }
    }
        
}


module yawsupport( e=4 )
{
   difference()
    {
   union()
    {
    translate( [0,10,0] )
    cube( [20+2*e,40,20] ,center = true);
    translate([0,0,-17+7/2] )
    cube( [20+2*e,20,7+0.01] ,center = true);
    translate([0,0,-17-e/2] )
    cube( [20+2*e,20,e] ,center = true);
    } 
    union()
    {
    cube( [20,100,20+2*7+0.01] ,center = true);
    translate([0,0,-13.5])
    cylinder( r=4,h=100,center = true,$fn=200);
    translate([0,-5,0])
    rotate([0,90,0])
    cylinder( r=2.5,h=100,center=true,$fn=200);
    
    translate([0,10,0])
    rotate([0,90,0])
    cylinder( r=2.5,h=100,center=true,$fn=200);
    
    translate([0,25,0])
    rotate([0,90,0])
    cylinder( r=2.5,h=100,center=true,$fn=200);
    }
}
    
}




module yawpouliemount( e = 4 )
{
    difference()
    {
    union()
    {
    translate( [0,10,0] )
    cube( [20+2*e,40,20] ,center = true);
    translate([0,0,-18+8/2] )
    cube( [45+2*e,20,8+0.01] ,center = true);
    translate([0,0,-18-7/2] )
    cube( [45+2*e,20,7] ,center = true);
    }
    union()
    {
    cube( [20,100,20+0.01] ,center = true);
    translate([0,0,-21.5])
    cylinder( r=radius608,h=7+0.01,center = true,$fn=200);
    translate([0,0,-14.5])
    cylinder( r=8,h=9+0.02,center = true,$fn=200);
    
    translate([0,-5,0])
    rotate([0,90,0])
    cylinder( r=2.5,h=100,center=true,$fn=200);
    
    translate([0,10,0])
    rotate([0,90,0])
    cylinder( r=2.5,h=100,center=true,$fn=200);
    
    translate([0,25,0])
    rotate([0,90,0])
    cylinder( r=2.5,h=100,center=true,$fn=200);
        
    for (deg = [0:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,-18])
                cylinder( r1=2,r2=2.0,h=14+0.02,center=true,$fn=200);
            }
            for (deg = [0:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,-15])
                cylinder( r=4.5,h=14+0.02,center=true,$fn=6);
            }
        
    }
    
    
    }
    
}

module yawpouliemountflat( e = 4 )
{
    difference()
    {
    union()
    {
    translate([0,0,-18+8/2] )
    cube( [95+2*e,20,8+0.01] ,center = true);
    translate([0,0,-18-7/2] )
    cube( [45+2*e,20,7] ,center = true);
    }
    union()
    {
    translate([0,0,-21.5])
    cylinder( r=radius608,h=7+0.01,center = true,$fn=200);
    translate([0,0,-14.5])
    cylinder( r=8,h=9+0.02,center = true,$fn=200);

    translate([45,0,-14.5])
    cylinder( r=2.5, h=20,center=true,$fn=200);
    translate([45,0,-16.5])
    cylinder( r=5.0, h=4,center=true,$fn=200);
    
    translate([-45,0,-14.5])
    cylinder( r=2.5, h=20,center=true,$fn=200);
    translate([-45,0,-16.5])
    cylinder( r=5.0, h=4,center=true,$fn=200);
        
    for (deg = [0:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,-18])
                cylinder( r1=2,r2=2.0,h=14+0.02,center=true,$fn=200);
            }
            for (deg = [0:180:(360-1)] )
            {
                rotate( [0,0,deg])
                translate([20,0,-15])
                cylinder( r=4.5,h=14+0.02,center=true,$fn=6);
            }
        
    }
    
    
    }
    
}

module yawsupportflat( e = 4 )
{
    difference()
    {
    union()
    {
    translate([0,0,-18+7/2-e/2] )
    cube( [75+2*e,20,7+0.01+e] ,center = true);
    translate([0,0,-18-e/2] )
    cube( [45+2*e,20,e] ,center = true);
    }
    union()
    {
    translate([0,0,-18+8/2] )
    cube( [33+2*e,20+0.01,8+0.03] ,center = true);
        
    translate([0,0,-14.5])
    cylinder( r=4,h=29+0.02,center = true,$fn=200);

    translate([35,0,-14.5])
    cylinder( r=2.5, h=20,center=true,$fn=200);
    translate([35,0,-17.5-e/2])
    cylinder( r=5.0, h=4+e,center=true,$fn=200);
    
    translate([-35,0,-14.5])
    cylinder( r=2.5, h=20,center=true,$fn=200);
    translate([-35,0,-17.5-e/2])
    cylinder( r=5.0, h=4+e,center=true,$fn=200);
        
    
    }
    
    
    }
    
}


module yawsupportflat2( e = 4 )
{
    difference()
    {
    union()
    {
    translate([0,0,-18+7/2-e/2] )
    cube( [45+2*e,20,9+0.01+e] ,center = true);
    translate([0,0,-18-e/2] )
    cube( [45+2*e,20,e] ,center = true);
    }
    union()
    {
    translate([0,0,-18+10/2] )
    cube( [13+2*e,20+0.01,8+0.03] ,center = true);
        
    translate([0,0,-14.5])
    cylinder( r=4,h=29+0.02,center = true,$fn=200);

    translate([15,0,-14.5])
    cylinder( r=2.5, h=20,center=true,$fn=200);
    translate([15,0,-17.5-e/2])
    cylinder( r=5.0, h=4+e,center=true,$fn=200);
    
    translate([-15,0,-14.5])
    cylinder( r=2.5, h=20,center=true,$fn=200);
    translate([-15,0,-17.5-e/2])
    cylinder( r=5.0, h=4+e,center=true,$fn=200);
        
    
    }
    
    
    }
    
}

module rollpouliemount( e = 4 )
{
    difference()
    {
    union()
    {
    cube( [20+e,20,50] ,center = true);
    translate([0,0,-29+8/2] )
    cube( [45+2*e,20,8+0.01] ,center = true);
    translate([0,0,-36.0+7/2] )
    cube( [45+2*e,20,7] ,center = true);
    }
    union()
        {
         translate( [0,0,e] )
         cube( [15+e,50,50] ,center = true);
            
         cylinder( r=8, h =100*e, center = true,$fn=200);
         translate([0,0,-36+7/2] )
         cylinder( r=radius608, h =7+0.01, center = true,$fn=200);
            
            
         translate( [0,0,5] )
            {
         rotate([0,90,0])
         cylinder( r=2.5, h =50,center=true,$fn=200);
         translate( [0,0,-15] )
         rotate([0,90,0])
         cylinder( r=2.5, h =50,center=true,$fn=200);
         translate( [0,0,15] )
         rotate([0,90,0])
         cylinder( r=2.5, h =50,center=true,$fn=200);
         
         for( deg=[0:180:359] )
         {
         rotate( [0,0,deg])
         translate([20,0,0])
         cylinder( r=2,h=100,center=true,$fn=200);
         
         rotate( [0,0,deg])
         translate([20,0,4])
         cylinder( r=4.5,h=83,center=true,$fn=6);
         }
          
            }
        }
    }
        
}


/*
support(4);
spacer(7.3);

drivepulley(35,30,7);



translate( [0,0,30] )
pouliemount();
*/
/*
translate( [0,0,20] )
pouliemountspacer();
/*
rotate([0,0,45])
translate( [0,0,70] )
    yawpouliemount();
*/
/*
rotate([0,0,45])
translate( [0,60,70] )
    yawpouliemountflat();
    */
/*
rotate([0,0,45])
translate( [0,-60,70] )
yawsupport();
*/
rotate([0,0,45])
translate( [0,90,70] )
yawsupportflat2();

/*
rotate([0,0,45])
translate( [0,0,120] )
    rollpouliemount();



translate( [0,0,-30] )
    roll();
/*
translate( [0,-90,0] )
gear(7,40,180,30);
translate( [0,-90,40] )
gear(7,40,0,-30);
*/
/*
translate( [0,-140.0,0] )
piniongear(7,10,3.1);
*/
