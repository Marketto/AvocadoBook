"""v22c: tabs on all 4 sides of every keycap, each sliding in a vertical channel of the base.
- top/bottom tabs (the existing ones, centred on the key): channel = two blocks beside the tab + the
  horizontal rib between the rows as back stop.
- left/right tabs (v22c): centred on the side, 0.7 mm out: in the 2.6 mm gap the tabs of two neighbours
  face each other and both slide in notches of the same rib (0.6 mm wall left between the notches).
The key spacing does not change. The tabs still hold the key under the frame (retention).
Requires the generator globals (exec'd before)."""
GT_CLR = 0.15         # v22c: clearance tab <-> channel, per side (was 0.2)
TAB_X = 0.7           # v22c: side tab out of the key wall; centred tabs of two neighbours face each other in the 2.6 gap
TAB_XW = 4.0          # v22c: side tab width (along y)
TAB_DROP = 1.5        # v22c: all tabs extend 1.5 mm below the keycap -> 2.5 mm of guided height (less tilt)
GRIB_Y = 3.2          # v26h: rib half-length in the gap: must stop before the spring channels (3.4) so the combs drop in from above (was 5.8)
GT_Z0 = KEY_BOT + REST_UP - TRAVEL - TAB_DROP - 0.1   # v22d: channel bottom = end stop (tabs bottom out 0.1 after the travel)


def side_tab_y(k, side):
    yc = (k["y0"] + k["y1"])/2
    return (yc - TAB_XW/2, yc + TAB_XW/2)      # v22c: centred on the side


def side_tabs(k):
    """Keycap additions (model pose): left tab up, right tab down; rooted in the side wall."""
    out = []
    for side in (-1, 1):
        ya, yb = side_tab_y(k, side)
        xe = k["x0"] if side < 0 else k["x1"]
        xa, xb = sorted([xe - side*1.2, xe + side*TAB_X])
        out.append(box(xa, xb, ya, yb, KEY_BOT, KEY_BOT + 1.0))
        xa, xb = sorted([xe - side*0.15, xe + side*TAB_X])        # extension below: outside the wall footprint only
        out.append(box(xa, xb, ya, yb, KEY_BOT - TAB_DROP, KEY_BOT + 0.01))
    for tx in key_tabs_x(k):                   # top/bottom tabs: same downward extension
        for ye, sy in ((k["y0"], -1), (k["y1"], 1)):
            ya, yb = sorted([ye - sy*0.15, ye + sy*TAB_L])
            out.append(box(tx - TAB_W/2, tx + TAB_W/2, ya, yb, KEY_BOT - TAB_DROP, KEY_BOT + 0.01))
    return union(out)


def guide_parts(klist):
    """Base additions (ribs in the x gaps, blocks beside the top/bottom tabs) and cuts (sliding channels)."""
    adds, cuts = [], []
    for k in klist:
        yc = (k["y0"] + k["y1"])/2
        for side in (-1, 1):
            xe = k["x0"] if side < 0 else k["x1"]
            xg = xe + side*KEY_GAP_X/2
            adds.append(box(xg - KEY_GAP_X/2 + 0.3, xg + KEY_GAP_X/2 - 0.3, yc - GRIB_Y, yc + GRIB_Y, GT_Z0 - 0.2, SPLIT))
            ya, yb = side_tab_y(k, side)
            xa, xb = sorted([xe - side*0.5, xe + side*(TAB_X + GT_CLR)])
            cuts.append(box(xa, xb, ya - GT_CLR, yb + GT_CLR, GT_Z0, SPLIT + 0.01))
        for tx in key_tabs_x(k):
            for ye, sy in ((k["y0"], -1), (k["y1"], 1)):
                ya, yb = sorted([ye + sy*0.3, ye + sy*2.0])
                for sx in (-1, 1):
                    xa, xb = sorted([tx + sx*(TAB_W/2 + GT_CLR), tx + sx*(TAB_W/2 + GT_CLR + 1.0)])
                    adds.append(box(xa, xb, ya, yb, GT_Z0 - 0.2, SPLIT))
                ca, cb = sorted([ye - sy*0.5, ye + sy*(TAB_L + GT_CLR)])
                cuts.append(box(tx - TAB_W/2 - GT_CLR, tx + TAB_W/2 + GT_CLR, ca, cb, GT_Z0, SPLIT + 0.01))
    return union(adds), union(cuts)
