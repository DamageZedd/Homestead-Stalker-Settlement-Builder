// Placement hologram vertex shader (homestead\hologram). Plain model transform for static and skinned
// visuals, passing the view-space normal and position on for the edge glow in homestead_hologram.ps.
#include "common.h"
#include "skin.h"

struct v2p_holo
{
	float2 tc0  : TEXCOORD0;
	float3 N    : TEXCOORD1;
	float3 P    : TEXCOORD2;
	float4 hpos : SV_Position;
};

v2p_holo _main( v_model I )
{
	v2p_holo O;
	O.hpos = mul( m_WVP, I.P );
	O.tc0 = I.tc.xy;
	O.N = mul( (float3x3)m_WV, (float3)I.N );
	O.P = (float3)mul( m_WV, I.P );
	return O;
}

/////////////////////////////////////////////////////////////////////////
#ifdef 	SKIN_NONE
v2p_holo	main(v_model v) 		{ return _main(v); }
#endif

#ifdef 	SKIN_0
v2p_holo	main(v_model_skinned_0 v) 	{ return _main(skinning_0(v)); }
#endif

#ifdef	SKIN_1
v2p_holo	main(v_model_skinned_1 v) 	{ return _main(skinning_1(v)); }
#endif

#ifdef	SKIN_2
v2p_holo	main(v_model_skinned_2 v) 	{ return _main(skinning_2(v)); }
#endif

#ifdef	SKIN_3
v2p_holo	main(v_model_skinned_3 v) 	{ return _main(skinning_3(v)); }
#endif

#ifdef	SKIN_4
v2p_holo	main(v_model_skinned_4 v) 	{ return _main(skinning_4(v)); }
#endif

FXVS;
