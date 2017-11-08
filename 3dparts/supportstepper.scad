module nemaPlate(wallThickness=3)
{
    wallThickness = 3;
    motorWidth = 45;
    bolt = 4;
    bolt2 = 5;
    difference()
    {
        union()
        {
            cube( [wallThickness, motorWidth, motorWidth], center=true);
           
        }
   rotate( [0,90,0]) 
        {
           translate([0, 0, -2])
				{
					translate([15.5, 15.5, 0])
						cylinder(r=bolt/2, h=wallThickness+5,$fn=200);
					translate([-15.5, 15.5, 0])
						cylinder(r=bolt/2, h=wallThickness+5,$fn=200);
					translate([15.5, -15.5, 0])
						cylinder(r=bolt/2, h=wallThickness+5,$fn=200);
					translate([-15.5, -15.5, 0])
						cylinder(r=bolt/2, h=wallThickness+5,$fn=200);

					cylinder(r=11.5, h=wallThickness+5,$fn=200);
                    rotate([0,0,90])
                    {
					translate([-11.5, 0, 0])
						cube([23, motorWidth, wallThickness+5]);
                    }
				}
        }
		
        
    }
}

e=3;

nemaPlate(e);
l=70;
sp = 30;

rotate([-90,0,0])
difference()
{
union()
    {
translate([20-e/2,0,-22-e/2])
cube([40,l,3],center=true);
translate([0,30-e,-0]) 
cube([3,16,45+0.01],center=true);
    }
union()
    {
    for (x = [5:1.0:34] )
    {
        if( round(x / 5) %2 !=0 )
        {
        translate([x,sp,0])
        cylinder(r=2.5,h=100,center=true,$fn=100);
        translate([x,-sp,0])
        cylinder(r=2.5,h=100,center=true,$fn=100);
        }
        
    }
        
}   
}
