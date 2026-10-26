-- homestead\hologram (r3/r4 - DX10/DX11)
-- Flat, alpha-blended tint for the placement hologram (homestead_hologram.script). Same stock
-- programs and pass setup as the engine's glass shader, with plain alpha blending so the colour
-- and opacity come from the texture (homestead_holo_ok / homestead_holo_bad).
function normal(shader, t_base, t_second, t_detail)
	shader:begin("model_distort4glass", "particle_hard")
		: sorting(3, true)
		: blend(true, blend.srcalpha, blend.invsrcalpha)
		: aref(true, 0)
		: zb(true, false)
		: fog(false)
		: distort(true)
	shader:dx10texture("s_base", t_base)
	shader:dx10sampler("smp_base")
end
