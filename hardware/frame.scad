dia = 14.5;
rod_l = 1200;

wall = 4;
clamp_d = dia + wall * 2;
clamp_h = 30;
screw = 4.5;

l = rod_l + 2 * dia;

plane_off = 100;
plane_l = rod_l - plane_off;

echo("rod", rod_l);
echo("plane", plane_l);
echo("outer", l);

$fn = $preview ? 42 : 100;

module rods() {
    // left/right
    for (x = [0, l])
    translate([x, 0, 0])
    cylinder(d = dia, h = rod_l);
    
    // top/bottom
    for (z = [0, l])
    translate([dia, 0, z - dia])
    rotate([0, 90, 0])
    cylinder(d = dia, h = rod_l);
    
    // plane
    translate([(l - plane_l) / 2, 0, -dia + (l - plane_l) / 2 - 1 * plane_off])
    cube([plane_l, 1, plane_l + 2 * plane_off]);
    translate([(l - plane_l) / 2 - 1 * plane_off, 0, -dia + (l - plane_l) / 2])
    cube([plane_l + 2 * plane_off, 1, plane_l]);
}

module clamp() {
    difference() {
        union() {
            hull()
            for (r = [0, 90])
            rotate([0, r, 0])
            translate([0, 0, dia])
            cylinder(d = clamp_d, h = clamp_h / 2);
            
            for (r = [0, 90])
            rotate([0, r, 0])
            translate([0, 0, dia])
            cylinder(d = clamp_d, h = clamp_h);
        }
        
        for (r = [0, 90])
        rotate([0, r, 0])
        translate([0, 0, dia])
        translate([0, 0, -20])
        cylinder(d = dia, h = clamp_h + 30);
        
        for (i = [0, 1])
        translate([i ? clamp_h * 3 / 4 + dia : 0, clamp_d / 2 + 1, i ? 0 : clamp_h * 3 / 4 + dia])
        rotate([90, 0, 0])
        cylinder(d = screw, h = clamp_d + 2);
    }
}

module frame() {
    %translate([-l / 2, 0, dia - l / 2])
    rods();
    
    for (r = [0 : 90 : 360])
    rotate([0, r, 0])
    translate([-l/ 2, 0, -l / 2])
    clamp();
}

if ($preview)
    translate([l / 2, 0, l / 2])
    frame();
else
    clamp();
