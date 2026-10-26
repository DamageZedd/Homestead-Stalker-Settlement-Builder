-- homestead\hologram (r3/r4 - DX10/DX11)
-- Alpha-blended tint for the placement hologram (homestead_hologram.script): colour and opacity from the
-- texture (homestead_holo_ok / homestead_holo_bad), plus a rim glow. A normal forward pass with depth
-- testing and no depth writes, set up like the Wearable Devices model shaders that also run on
-- script attachments. It is not a "distort" shader: those draw offsets into the distortion buffer
-- instead of colour, which refracts the scene rather than tinting it.
function normal(shader, t_base, t_second, t_detail)
	shader:begin("homestead_hologram", "homestead_hologram")
		: fog(false)
		: zb(true, false)
		: blend(true, blend.srcalpha, blend.invsrcalpha)
		: sorting(1, true)

	shader:dx10texture("s_base", t_base)
	shader:dx10sampler("smp_base")
end
