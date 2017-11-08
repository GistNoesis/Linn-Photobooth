/*                                                                              
mega 2560, RAMPS 1.4 and 40x40 fan box
author @mashirito                           

https://www.thingiverse.com/discostu/about                                      
https://cults3d.com/en/users/mashirito/creations                                
https://www.myminifactory.com/users/mashirito                                   
                                                                                
Copyright 2017 Sergio Casanova sercasa@gmail.com                                
 * This program is free software: you can redistribute it and/or modify         
 * it under the terms of the GNU General Public License as published by         
 * the Free Software Foundation, either version 3 of the License, or            
 * (at your option) any later version.                                          
 *                                                                              
 * This program is distributed in the hope that it will be useful,              
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
 * GNU General Public License for more details.                                 
 *                                                                              
 * See <http://www.gnu.org/licenses/>.                                          
                                                                                
This desing is shared under terms of CC License - Attribution-NonCommercial-ShareAlike
https://creativecommons.org/licenses/by-nc-sa/4.0/                              
*/

$fn=40;

// Assamble or disassable parts
assambled=false;
// print mask 
mask=true;
// print main box
mainbox=true;
// cover 
coverfan=true;

module mountbar()
{
    difference()
    {
        cube([4,20,120],center=true);
        union()
        {
            translate([0,0,50] )
            rotate([0,90,0])
            cylinder( r=2.5, h=10,center=true);
            rotate([0,90,0])
            cylinder( r=2.5, h=10,center=true);
            translate([0,0,-50] )
             rotate([0,90,0])
            cylinder( r=2.5, h=10,center=true);
        }
    }
    
}

if(mainbox==true){
    union()
    {
    main_box();
    translate([0,23.01,-2.0])
    mountbar();
    translate([0,-58,-2.0])
    mountbar();
    }
}
if (assambled==true){
    if (mask==true){
        mask_items();
    }
    if(coverfan){
        cover_fan();
    }   
}
else{
    if(mask==true){
        translate([0,0,-140]) mask_items();
    }
    if(coverfan==true){
        translate([0,0,-155]) cover_fan();
    }
}

module mask_items(){
    rotate([0,90,0]) import("./RAMPS1_4.STL", convexity=3);
    translate([2,-35,-62])  fan40();
}

module main_box(){
difference(){
    color("blue"){
        translate([-2,-50,-64])  roundedcube(49,65,122,2);
    }
    
    color("red"){
        ramps_mask(true);
        translate([0,0,-20]) ramps_mask(false);
    }
    
    // frontal air holes 
    hull(){
        translate([20,0,50]) cylinder(10,2,2);
        translate([40,0,50]) cylinder(10,2,2); 
    }
    hull(){
        translate([20,-8,50]) cylinder(10,2,2);
        translate([40,-8,50]) cylinder(10,2,2); 
    }
    hull(){
        translate([5,8,50]) cylinder(10,2,2);
        translate([40,8,50]) cylinder(10,2,2); 
    }
    hull(){
        translate([5,-16,50]) cylinder(10,2,2);
        translate([40,-16,50]) cylinder(10,2,2); 
    }
    //////////////////////////////

    
    // cover holder  hole
    translate([3,-46,-65])  cylinder(55,1.5,1.5);
    translate([0.5,-49,-60]) cube([5,15,2.5]);
    
    // box holder screws
    color("yellow"){
        translate([-10,0,-50]) rotate([0,90,0]) cylinder(65,2,2);
        translate([-10,-35,-50]) rotate([0,90,0]) cylinder(65,2,2);
        translate([-10,0,40]) rotate([0,90,0]) cylinder(65,2,2);
        translate([-10,-35,40]) rotate([0,90,0]) cylinder(65,2,2);
    }
    //upper connector hole
    hull(){
        translate([30,-18,-50]) rotate([0,90,0]) cylinder(25,7,7);
        translate([30,-18,40]) rotate([0,90,0]) cylinder(25,7,7);
        }
    hull(){
        translate([30,-38,-50]) rotate([0,90,0]) cylinder(25,7,7);
        translate([30,-38,40]) rotate([0,90,0]) cylinder(25,7,7);
        }
      hull(){
        translate([30,2,-50]) rotate([0,90,0]) cylinder(25,7,7);
        translate([30,2,40]) rotate([0,90,0]) cylinder(25,7,7);
        }
}

    // cover holder holes
    
    difference(){
        color("blue"){
                union(){
                translate([41,11,-64])  cylinder(8,3,3);
                translate([41,-46,-64])  cylinder(8,3,3);
            }
        }
    
       color("red"){
                //translate([3,-46,-58])  cylinder(15,1.5,1.5);
                translate([41,11,-68])  cylinder(15,1.5,1.5);
                translate([41,-46,-68])  cylinder(15,1.5,1.5);
            }
    }
    
    
}

module cover_fan(){
    difference(){
        color("blue"){
            translate([-2,-50,-64])  roundedcube(49,65,2,2);
        }
        //fan screws
        color("red"){
            translate([6,-31,-68])  cylinder(15,1.5,1.5);
            translate([6,1,-68])  cylinder(15,1.5,1.5);
            translate([38,1,-68])  cylinder(15,1.5,1.5);
            translate([38,-31,-68])  cylinder(15,1.5,1.5);
        }
        
        // cover screws
        color("red"){
            translate([3,-46,-68])  cylinder(15,1.5,1.5);
            //translate([3,11,-68])  cylinder(15,1.5,1.5);
            translate([41,11,-68])  cylinder(15,1.5,1.5);
            translate([41,-46,-68])  cylinder(15,1.5,1.5);
        }
        
        // big fan hole
        color("red"){
            translate([22,-15,-68])  cylinder(15,18,18);
        }
    }
    //fan protector
    difference(){
        translate([22,-15,-64])  cylinder(2,15,15);
        translate([22,-15,-65])  cylinder(5,13.5,13.5);
    }
    difference(){
        translate([22,-15,-64])  cylinder(2,10,10);
        translate([22,-15,-65])  cylinder(5,8.5,8.5);
    }
    translate([22,-15,-64])  cylinder(2,4,4);
    
    // cross fan holder
    translate([22,-15,-63])  cube([45,2, 2], center=true);
    translate([22,-15,-63])  cube([2,45, 2], center=true);
 
    
    
}

module ramps_mask(button){

        
        //USB
        translate([2.2,-8,-40]) cube([12.5,15,100]);
        //mega power
        translate([2.8,-34,-40]) cube([12,11,100]);
        //ramps power
        translate([15.75,-48,-40]) cube([16.5,25,100]);
        //ramps rails
        translate([14.3,-49,-50]) cube([2.4,62.5,105]);
        //ramps inner space
        translate([11,-47.8,-50]) cube([32,60,105]);
        //mega inner space
        translate([0,-42,-50]) cube([13.5,55,105]);
        if(button==true){
            //ramps button
            translate([19.8,-40,18]) rotate([90,0,0]) cylinder(13,2.5,2.5);
            
            //button guide
            hull(){
                translate([19.8,-36,19]) rotate([90,0,0]) cylinder(13,2,2);
                translate([19.8,-36,-79]) rotate([90,0,0]) cylinder(13,2,2);
            }
        }
}


module roundedcube(xdim ,ydim ,zdim,rdim){
    hull(){
        translate([rdim,rdim,0])cylinder(h=zdim,r=rdim);
        translate([xdim-rdim,rdim,0])cylinder(h=zdim,r=rdim);
        
        translate([rdim,ydim-rdim,0])cylinder(h=zdim,r=rdim);
        translate([xdim-rdim,ydim-rdim,0])cylinder(h=zdim,r=rdim);
    }
}

module fan40(){
    difference(){
        roundedcube(40,40,10,3);
        translate([4,4,-4])  cylinder(15,1.5,1.5);
        translate([4,36,-4])  cylinder(15,1.5,1.5);
        translate([36,36,-4])  cylinder(15,1.5,1.5);
        translate([36,4,-4])  cylinder(15,1.5,1.5);
    }    
    }





