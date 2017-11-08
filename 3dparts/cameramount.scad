
e=3;

module cameramount()
{
difference()
{
union()
{
translate([0,0,10+e/2])
cube([60,20,e],center=true);
translate([0,0,-10-e/2])
cube([60,20,e],center=true);

translate([10,0,0])
cube( [e,20,20],center=true);
}
union()
{
  translate( [-24,0,0])
  cylinder( r = 2.5,h=40,center =true,$fn=200);
  cylinder( r = 2.5,h=40,center =true,$fn=200); 
  
  translate( [24,0,0])
  cylinder( r = 3.0,h=40,center =true,$fn=200);
}

}

}

module polemount()
{
    d=25;
    union()
    {
    difference()
    {
    union()
    {
    difference()
    {
    cylinder( r = d/2+e, h = 10, center=true,$fn=200);
    cylinder( r = d/2, h = 12, center=true,$fn=200);
    }
    
    translate([0,20,0])
    cube([10,12,10],center=true);
    }
    union()
    {
    translate([0,20,0])
    cube([4,18,12],center=true);
    translate([0,21,0])
    rotate([0,90,0])
    cylinder( r = 3,h=50,center=true,$fn=200);
    }
    }
    
    translate([0,-d/2-(20+e)/2,-10/2+e/2])
    difference()
    {
    cube([40,20+e,e],center=true);
    union()
    {
     translate([15,-e/2,0])
     cylinder(r=2.5,h=2*e,center=true,$fn=200);
     translate([-15,-e/2,0])
     cylinder(r=2.5,h=2*e,center=true,$fn=200);       
     }
    }

        
    }
}

polemount();
