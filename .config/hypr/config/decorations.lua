-- Look and feel configuration

hl.config({
    general = {
        gaps_in = 3,
        gaps_out = 8,
        border_size = 2,
        extend_border_grab_area = 10,
        resize_on_border = true,
        col = {
            active_border = {
                colors = { CACHYGREY, CACHYGRAY },
                angle = 45,
            },
            inactive_border = "rgba(666666ff)",
        },
    },
    group = {
        col = {
            border_active = CACHYGREY,
            border_inactive = "rgba(666666ff)",
            border_locked_active = CACHYGRAY,
            border_locked_inactive = "rgba(666666ff)",
        },
        groupbar = {
            col = {
                active = CACHYGREY,
                inactive = "rgba(666666ff)",
                locked_active = CACHYGRAY,
                locked_inactive = "rgba(666666ff)",
            },
        },
    },
    decoration = {
        dim_special = 0.3,
        rounding = 10,
        active_opacity = 0.95,
        inactive_opacity = 0.85,
        fullscreen_opacity = 1,
        blur = {
            size = 5,
            passes = 4,
            special = true,
        },
    },
})
