panel_w = 127.8;
panel_d = 13;

panel_hole_dia = 2.5;
panel_hole_dist_x = 114.4 - panel_hole_dia;
panel_hole_dist_y = 92.4 - panel_hole_dia;

hole_off_x = (panel_w - panel_hole_dist_x) / 2;
hole_off_y = (panel_w - panel_hole_dist_y) / 2;

panel_nub_d = 3.0;
panel_nub_h = 4.0;
panel_nub_off_x = 24.25 - (panel_nub_d / 2);
panel_nub_off_y = 10.0 - (panel_nub_d / 2);
panel_nub_hole = panel_nub_d + 1.0;

strip_w = hole_off_x * 2 + 10;
strip_d = 6.0;
strip_hole_d = 4.0;

foot_h = 10;
foot_plate_h = foot_h + hole_off_y + 10;
foot_d = strip_d;
foot_l = 100.0;

conn_h = hole_off_y * 2 + 50;
conn_w = strip_w;
conn_d = foot_d;
conn_hole_d = strip_hole_d;

pi_width = 85;
pi_height = 56;
pi_hole_dist_x = 58;
pi_hole_dist_y = 49;
pi_hole_off_x = 3.5;
pi_hole_off_y = 3.5;
pi_hole = 2.8;

pi_off_x = 10;
pi_off_y = 25;
pi_mount_dist = 10;
pi_mount_w = 15.0;
pi_mount_d = foot_d;

$fn = 42;

module holes(h, d1 = pi_hole, d2 = pi_hole) {
    for (x = [0, pi_hole_dist_x])
    for (y = [0, pi_hole_dist_y])
    translate([pi_hole_off_x + x, 0, pi_hole_off_y + y])
    rotate([90, 0, 0])
    cylinder(d1 = d1, d2 = d2, h = h);
}

module pi() {
    cube([pi_width, 2.0, pi_height]);
    
    translate([0, 10, 0])
    holes(20);
}

module panel() {
    difference() {
        cube([panel_w, panel_d, panel_w]);
        
        for (x = [0, panel_hole_dist_x])
        for (y = [0, panel_hole_dist_y])
        translate([hole_off_x + x, -1, hole_off_y + y])
        rotate([-90, 0, 0])
        cylinder(d = panel_hole_dia, h = panel_d + 2);
    }
    
    // actually only bottom-left and top-right
    for (x = [panel_nub_off_x, panel_w - panel_nub_off_x])
    for (y = [panel_nub_off_y, panel_w - panel_nub_off_y])
    translate([x, 0, y])
    rotate([90, 0, 0])
    cylinder(d = panel_nub_d, h = panel_nub_h);
}

module foot() {
    translate([0, -strip_d * 2, 0])
    difference() {
        translate([-strip_w / 2, 0, -foot_h])
        cube([strip_w, strip_d, foot_plate_h]);
        
        for (x = [-1, 1])
        translate([x * hole_off_x, -1, hole_off_y])
        rotate([-90, 0, 0])
        cylinder(d = strip_hole_d, h = strip_d + 2);
    }
    
    translate([-strip_w / 2, -strip_d * 2 - foot_l / 2 + foot_d / 2, -foot_h - foot_d])
    cube([strip_w, foot_l, foot_d]);
    
    for (d = [-strip_d * 2 - 5, -strip_d])
    translate([-strip_w / 2, d, -foot_h])
    cube([strip_w, 5, 5]);
}

module foot_strip() {
    translate([0, -strip_d, 0])
    difference() {
        translate([-strip_w / 2, 0, 0])
        cube([strip_w, strip_d, panel_w]);
        
        for (x = [-1, 1])
        for (y = [0, panel_hole_dist_y])
        translate([x * hole_off_x, -1, hole_off_y + y])
        rotate([-90, 0, 0])
        cylinder(d = strip_hole_d, h = strip_d + 2);
    }
    
    difference() {
        for (x = [-1, 1])
        scale([x, 1, 1])
        for (y = [0, panel_w - 15])
        translate([strip_w / 2, -strip_d, y])
        cube([20, strip_d, 15]);
        
        for (x = [-panel_nub_off_x, panel_nub_off_x])
        for (y = [panel_nub_off_y, panel_w - panel_nub_off_y])
        translate([x, 1, y])
        rotate([90, 0, 0])
        cylinder(d = panel_nub_hole, h = strip_d + 2);
    }
}

module conn() {
    difference() {
        translate([-conn_w / 2, -conn_d, -conn_h / 2])
        cube([conn_w, conn_d, conn_h]);
        
        for (x = [-1, 1])
        for (y = [0, -hole_off_y * 2])
        translate([x * hole_off_x, -conn_d - 1, hole_off_y + y])
        rotate([-90, 0, 0])
        cylinder(d = strip_hole_d, h = strip_d + 2);
    }
}

module foot_half() {
    difference() {
        foot();
        
        translate([-50, -100, -50])
        cube([50, 200, 200]);
    }
}

module foot_strip_half() {
    difference() {
        foot_strip();
        
        translate([-50, -10, -5])
        cube([50, 20, 200]);
    }
}

module conn_half() {
    difference() {
        conn();
        
        translate([-50, -10, -100])
        cube([50, 20, 200]);
    }
}

module pi_mount_piece(l, z) {
    translate([0, 0, z])
    difference() {
        translate([0, -pi_mount_d - strip_d - conn_d, 0])
        cube([panel_w, pi_mount_d, pi_mount_w]);
        
        for (x = [hole_off_x, panel_w - hole_off_x])
        translate([x, -strip_d - foot_d - pi_mount_d - 1, pi_mount_w / 2])
        rotate([-90, 0, 0])
        cylinder(d = strip_hole_d, h = strip_d + 2);
    }
    
    difference() {
        // TODO hardcoded
        for (x = [32, (pi_height + panel_w) / 2 - 11])
        translate([x + pi_off_x, -pi_mount_d - strip_d - conn_d, ((sign(l) < 0) ? l : pi_mount_w) + z])
        cube([pi_mount_w, pi_mount_d, abs(l) + 0.1]);
        
        translate([(pi_height + panel_w) / 2 + pi_off_x, -2 - strip_d - foot_d - conn_d - pi_mount_dist, pi_off_y])
        rotate([0, -90, 0])
        translate([0, 25, 0])
        holes(20, 3.5, 3.5);
    }
    
    // TODO missing slot nub holes!
}

module pi_mount() {
    %translate([(pi_height + panel_w) / 2 + pi_off_x, -2 - strip_d - foot_d - pi_mount_d - pi_mount_dist, pi_off_y])
    rotate([0, -90, 0])
    pi();
    
    color("red") {
        // TODO hardcoded
        pi_mount_piece(7, hole_off_y - pi_mount_w / 2);
        pi_mount_piece(-20, panel_w - hole_off_y - pi_mount_w / 2);
    }
}

psu_w = 98.3;
psu_h = 129.2;
psu_d = 40.1;

psu_hole_dia = 4.0;
psu_hole_w = 35.5 - 2.4;
psu_hole_h = 44.4 - 2.4;
psu_hole_x = 29.85 + 1.2;
psu_hole_y = 34.85 + 1.2;

psu_y_off = 30;
psu_mount_w = 15;
psu_mount_d = foot_d;

module psu_holes() {
    for (x = [0, psu_hole_w])
    for (y = [0, psu_hole_h])
    translate([x + psu_hole_x, -1, y + psu_hole_y])
    rotate([-90, 0, 0])
    cylinder(d = psu_hole_dia, h = psu_d + 10);
}

module psu_mount_piece(l, z) {
    difference() {
        translate([0, 0, z])
        union() {
            translate([0, -psu_mount_d - strip_d - conn_d, 0])
            cube([panel_w, psu_mount_d, psu_mount_w]);
            
            for (x = [0, psu_hole_w])
            translate([x + (panel_w - psu_w) / 2 + psu_hole_x - psu_mount_w / 2, -psu_mount_d - strip_d - conn_d, ((sign(l) < 0) ? l : psu_mount_w)])
            cube([psu_mount_w, psu_mount_d, abs(l) + 0.1]);
        }
        
        translate([0, 0, z])
        for (x = [hole_off_x, panel_w - hole_off_x])
        translate([x, -strip_d - foot_d - psu_mount_d - 1, psu_mount_w / 2])
        rotate([-90, 0, 0])
        cylinder(d = strip_hole_d, h = strip_d + 2);
        
        translate([(panel_w - psu_w) / 2, -psu_d - strip_d - foot_d - psu_mount_d, psu_y_off])
        psu_holes();
        
        // TODO missing slot nub holes!
    }
}

module psu_mount() {
    %translate([(panel_w - psu_w) / 2, -psu_d - strip_d - foot_d - psu_mount_d, psu_y_off])
    difference() {
        cube([psu_w, psu_d, psu_h]);
        
        translate([0, -5, 0])
        psu_holes();
    }
    
    color("red") {
        // TODO hardcoded
        psu_mount_piece(46, hole_off_y - psu_mount_w / 2);
        psu_mount_piece(0, panel_w - hole_off_y - psu_mount_w / 2);
    }
}

module two_by_two() {
    %for (x = [0, panel_w])
    for (y = [0, panel_w])
    translate([x, 0, y])
    panel();
    
    pi_mount();
    
    translate([panel_w, 0, 0])
    psu_mount();
    
    translate([panel_w, 0, 0]) {
        color("green")
        for (y = [0, panel_w])
        translate([0, 0, y])
        foot_strip();
        
        color("yellow")
        foot();
    }
    
    for (y = [0, panel_w])
    translate([0, 0, y]) {
        color("cyan")
        foot_strip_half();
        
        color("orange")
        if (y == 0)
        foot_half();
        
        translate([panel_w * 2, 0, 0])
        scale([-1, 1, 1]) {
            color("cyan")
            foot_strip_half();
            
            color("orange")
            if (y == 0)
            foot_half();
        }
    }
    
    color("magenta")
    translate([panel_w, -strip_d, panel_w])
    conn();
    
    color("blue")
    for (x = [0, panel_w * 2])
    translate([x, -strip_d, panel_w])
    scale([x == 0 ? 1 : -1, 1, 1])
    conn_half();
}

module three_by_one() {
    %for (x = [0, panel_w, panel_w * 2])
    translate([x, 0, 0])
    panel();
    
    pi_mount();
    
    translate([panel_w * 2, 0, 0])
    psu_mount();
    
    // TODO filler pieces for top gap
    
    for (x = [panel_w, panel_w * 2])
    translate([x, 0, 0]) {
        color("green")
        foot_strip();
        
        color("yellow")
        foot();
    }
    
    color("cyan")
    foot_strip_half();
    
    color("orange")
    foot_half();
    
    translate([panel_w * 3, 0, 0])
    scale([-1, 1, 1]) {
        color("cyan")
        foot_strip_half();
        
        color("orange")
        foot_half();
    }
}

two_by_two();
//three_by_one();

//foot_strip();
//foot_strip_half();

//foot();
//foot_half();

//conn();
//conn_half();

//pi_mount();
//psu_mount();
