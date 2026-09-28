"""V115 Adaptive Sovereign: Top-10 Leaderboard Master Champion.
Incorporates:
1. Dynamic Early & Mid-Game Town Shop Routing:
   - Early Yarn Store (Day 4/7): Routes to V50 Wool Powerhouse (11 Sheep)
   - Otherwise: Routes to Lizs Multi-Livestock Powerhouse (6C/4S/7G)
2. Mid-Game Yarn Store Pivot:
   - If Yarn Store unlocks on Day 10+ (step 216+), automatically pivots subsequent
     animal purchases from GOOSE to SHEEP (reaching 9 Sheep), capturing full wool bonuses!
3. Milk Sink Cow Adaptation:
   - When Milk sinks (PIZZA_SHOP, ICE_CREAM_SHOP, SMOOTHIE_SHOP) are open without Yarn Store,
     swaps 1 Sheep for 1 Cow on Day 6 to maximize high-value milk revenue.
4. Step 717-718 Terminal Harvest Rush & Shed Drop:
   - Overrides worker actions at steps 717-718 to rush all carried inventory into the shed,
     guaranteeing 100% of carried inventory is sold at step 718 (salvaging +800-1200 coins).
5. V92 Day-23 Hour-23 Shed Capacity Overflow Guard.
6. Step-629 Early Continuous Shed Clearance on v56 route.
7. Late-Collision Terminal Overlay + Market Impact Slot Ordering.
8. Full Seat 1 Normalization.
"""

import base64
import copy
import json
import math
import sys
import types
import zlib


def _pkg(name):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = "<bundled-package:" + name + ">"
        module.__package__ = name
        module.__path__ = []
        sys.modules[name] = module
    return module


def _load(name, source):
    parent, _, child = name.rpartition(".")
    if parent:
        _pkg(parent)
    module = types.ModuleType(name)
    module.__file__ = "<bundled:" + name + ">"
    module.__package__ = parent
    sys.modules[name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    if parent:
        setattr(sys.modules[parent], child, module)
    return module


_MODULES = json.loads(zlib.decompress(base64.b85decode(
(
    'c%1Eh4SO56(coX%I(JV=o1`T<Usc0Ar#MRECwAqNowwIl(nGJvrL?aplHroJRiFR+%@=?fES4Wia=rG%HZr*j3<khpFqkiVd{7M+'
    '<$PK7-W}`@7PHl|7~B*$v&HS8D)Pnf`oUrLV7!>!WP`zYwOlQV!5}Md=Cj2z%cs-XGGCUnX>~r8XT#b2_I&#C=+&#NpM5-kFwPe@'
    '#o`>GoSi?w$L9|&I@$Sy>wG$@=rR4g$ro>nCI9|(J{=X~Y*EZ7`R!mno0P-bRz9S5+K1=U3_e&u-pnrjQ~XrRVh&B;l+)Ht{-L$k'
    '$;#;x3-zvwW$XL_zCVA^$@bdWYyp4UoorG}J^ZYj?Y9H8MFCx&Qm=ZWqL||sSN04+T_6<fmsFApjNADX8hY?<|4)Nuu>g$n36ADD'
    '{qN+mDi-f(^t!X@<Ti6fve~<00X?s>RaK0#OL%i#WB??~FDFz!<C*E5PtT{X;T;V9q_`=jJQrD6VVB`2{KzK&xrFhY7w~7g%w}Vl'
    'wp$t8Y`MsXMK8;q!NlbN?foL3LsMUOvOF8E77M7+y(yM?c2kUI<*0+5&0*57i$ykHT|ysWXr{}>Y?8e%m)Af&+1u&teL1~Cq|c|b'
    '`Fu9TW=m|mT;3wiJOI$zHe?kMmi)NMm)H32eERD6`SYXio*%=Mw|EB5AG~^fdi1yNj!#ejjuU<U;KlLtlfTN>XU~7)Z+|;EdCuRC'
    '|MD03;wryBd2#gmgx@?pIz2skE#-eaK9a9L9G|{^_Wap@9-mS@nE98dC*S}4^!4DozYmW7`s~Hgb0+?$Cx1hd*3G{9@%Z>9KMWZB'
    '<>chmF+U_^U<Lf;`OmKhe>;BmmmgmftVGuivxDBA$6Gpim_6xz86Hx*wjei)<qrHaYV|PN?|o4l2YmX(KXoI5PZdZW8~ad?l6wOk'
    'dvWx?1}CTAAD<$F*x!R0{PFnv!PBFcM^B%<{yRO}<Eh0pKA5g<E{jF$T|QYA9bESLYO?I__4eGFUoLJB^?I$~JwO>xX8Dq<$;vD~'
    '42$_PYrVdm7srdmY|+X717Fkk_F-+!OIv1H3;1$O6xb`PaXBrQMT?)evtm*ep`!0ZbzO`G`EXcNRqJw=FGho^{72#1yv`?Mz&O0f'
    '9zV_wOuHWgb}cFnT&k0~Z|zR>dd;g)v!RxI{3+m{Ps*$5fH=1BK41ia>+*trkuQhW#HuFcyCTEVux3}V_8n(f6gT;NF1#UwsVPVK'
    '5;)v^QH;wEJ;xUiBrNt4-t?1<7n#t<Pco~>#()_C+2E{LR?qJ=v(NfikY;I*>*M}ZLG@6Jo?xZ33#xT?5lSLq;p;O7eSvKX2H(&&'
    'LT`l*K7Mk9H!p@u>JAp6GSUZWQZ_@?WZRJjyuf;8wQTXA*ebR-V1q5tyEb6tT2{nO?|Q`t*dIo%v#=*;V*ms!7-&47UKK5mbXS3F'
    'yM`E*v#`BiB$0G)8B5<*3`F{ZFwO|bY%zinwRH$VegQ~Qm9s;K<;6t=(#aDM%m|9b*41%idSR9z7Y&PIzL@<NwN0xVsSY+xqEEXn'
    'UUE4Y#Vgp`zdt>B`S|7Yqo>EfCg!uMTtc<?*Ci~S;zKb6=_|V|0LOyX2xDYc#=ii)&le@gHHB$Jo?$aU_Dub*w2Wie=J4~jxIN62'
    '07sl$B(_irXA??xGJXwHIx2_DmbB(1KA0cVaJvUQ`=)BOJ*T6^Gkpg#%4|^<e#Kchsz7S3(rlv8f+UCI5-kF#0e#uK0D<#iOTAAl'
    'ewhK0GZ7wttwRj!1EHEy5r+_%%W^{fQwY$b1OccGi8&V)q$2x!4ny42;C0g$hpWX+6pEoAI@t<#%z<!nn6LtN_+kO09E<qE(5P1S'
    'Eo0!vn6NOf)a+;o%oRZPoUV%S)WHGFJ;*ZxcVQX_K@`O4a#}6(>9Fw4cd{1JM<-jZK=N)AG8#SPy$2hSfU&p*1dzI2#WNxg^JM>`'
    'ZBS}qwKiimbrS&X<Ac^-_Dvsvexs)gH)4AJK|epcy=ZS9r_ZuiC3GAn>8hL-C<z|)zUpK+*_xGs_%oZl1G-YY>-ovkpN_xpVq+TK'
    ')e2|>P8_eV7e$c`VagW377<`q`oa`?SwM@~WHx+@XCROsa)4XGyNQOzOciHmgmOh#f=F+G1#qR=9H|Q*_SQ|UqRI{}{<a%b^=9LE'
    'IU>BZ%nU!<F*LVU5=>1IxR7d+o8jk^>8a`f&=+nA=MQl5KrFWnyB&#$QaVxxUQ8Nb5-prRAc8|WQ)Sw?O5+uQkfA9JYX8C(L0W(!'
    'j$+R~MDKGr5ayFXwOp)*c!-RSUBDY(|9pB}J9(Ms>hSgS1V`l)@kPWgniyPt_DK>4IDaGE{1r~VsnR1&cG$BH&2Kwh77GZUehagX'
    '{2T^5ZZlo?`~jDPIT3bYS0jF69)O=ZUDI5cgO>X&ieFYm#oITMwVurb*iS?xjcMTtiwye~;MPa9^_VI;ZqYn;v^vOROq|w{xtns7'
    'o!ae=q4%oTxbSIzqw2q`a?*6rx)nsC>WkS7319HB=ihEtt!`RgDC!Xpfb|zM2?0&x9_hL~22Q_)?bS)yLr9FPZ~qKCg+g?|NRL$Z'
    'D1fp0FIPMW%uW|H0HJ+W0nxT<XUJn<@HZ$rzJn!l2}|GW#H!VNKDqTrNvBT2E;?}&RuqV8{~TG_>$#k~yblwpWM(BQBO|Px4{1D*'
    'dEvkwW_!IoPf<umPRaEt2vdvMdpg1Rmd$~(F47%ZS|!Gchdl%{)*K0*xDAl7Jc9=pG3TyrpNfxdy-bIT8ER^QiM14$!>7!cf!DQr'
    'Fz>~pRi|F6jN+pVUZPd^>I}<XWRG~op(4twl~lX8Wic5IkWW=i74eE=URp=k@!0h!!-5zAuZHS1T_M3?DD{3yy>;D_BGg0Z9jr-W'
    '26yczG^&b^iv|1wQGPMV-{s{bhh>TNe#n71QgiLmvKl~#o#7I$tWuS+Rv8WtSJNDKHd;2W9nvRNiG$)^?MO(A!(wN2xLUQVRlZHS'
    ';}{gl7)q>Al0+w#Fj%Z0CGzp{_Xe0fg6f4`*Ao3pENaAKj3mYrpq8^<CnCxupt8&xEiwYQetk&~yvWR?l4u~%(HRwH!c3RDTon0R'
    'L$Qjaw%6r#Hdb0q`J^*|y?eBP?YkKQ9XVUl10eJZP4U%i0eh~zZM$miu)c;9*ewR5Qf64~z}s(jc0aQxT^T0UzN5-y3{%FhC&d`q'
    'UwVaCc=DBzF0ZcF74!$<`jq6CRSTQJBT1J51-STm1cK+oP;5UG+qcC~2*YAI6u4xqVcy9uag6^_&bju%MMo-wpxdquwUb>2ti{tB'
    'La4Wz6n$77vk9z9c!I<Hu)}7#VbOoRSQS<@dR0s&S@Eubqh-*T3FrTFHoTtA@T`l9O*{ybWo^b5MwFxKvXLlY`i;tcE=DK){yJr+'
    '*ZB<#7PtceIfbfGy?K4$keOL{Rg;F&5~C{yGz?vp(RCU-qXCN*x=~G7XK(FZLgNRdaLB5qNW5qDl~*1I#Z`oh)z>I~N>v>ncBf>~'
    'OVgPMpD_;ZOpTJCo3c+%nFh?8l!8uCn~)UMlJv)czE(frJX%pcRz(2rzUnvqY;Utt4d*mVNLf7Ds<nMMlt787HCz+iYhuhb^+YwC'
    '5m|6M4?T8~Y9fGf^U?^ZYiL0sh!f+65)V1<dyj~Kbpz{<h^~o*!l1=Mnj>mG3%!~$2tN-qWewKD2*p#SX@F8M$Y?p4UG2~PAu$4='
    'T_1qTdifk32U;!aPABW82BH(4d|ej^0PaYw1v0Km*qSgF;Acd{XO75YFk+JG;Q#AKYXlzlBjKBB4nzfEEkV@i*<mn2D|M3WCS1?0'
    'w0r^*!00y3B`kXge8F;q-;Wv8TBhz<?KuLC*%N{fLlDue5_trK>#kQh^O!{SqDCCyaEGFU6a(nxBY7V--{h=CpcC^~n>#s7+|1q;'
    'gXQdfz8ERp{W4#`8iE~+739(p(Z;)Cp0u#nQll>C1p5oW;)0@*@$G<c)}Q1zm!llO1M@x1NVcHwEUJ7!CKH~KTyhHw%l&lU_Pn66'
    '1bm67b1QN_LOnPd)%Es(=Q&jUe^BU$f_{bL;p7z^h(557fM3T9;M>grj*lFGM>POwl(^jl;IAjAuYV*6I2q`^U?6<E8N#cRpB02h'
    '0Yc4;rPhzL5OlIBRGSii3DE6=B1_5?$CDs><I40_KVpUT^!DOx`r#t`11?^+ht#$rM@SwCOVXOa99iFhP_!)nfr6d)E8_#bl`+vh'
    '%?gnxz=jv)2n0oRIKwL5#<;xB$p?&WEYN%|-W((WUf!}_-B<fx-$jaqaii+OL0Vt!f7L-)39lQshVjwAovnKZ<E!I5_<H>)rERc*'
    '(0@1c^shCTtJlsU<>RN=4@E@Q$oSi>nS8w(OIaFzJIlEewD}a!TIBBsVN3CLgtk2y;91e5-N_8Xmajyr7YjaZZPsPBvp6fWcMF%3'
    'h7e58=IQ>0mPp}PkH<kg9XFUVX^^}YrWFjLa{Tl5i~uyb^Sb3?t$&^aZ*Ak|<!WtlPW>VKH14~&=T&|e#=WPy<-SyaUUeI6?Z!En'
    'q|O^w{M$BA_QJvX7Vtvs{Lp(qwT(anJ98#lC1uj-hTWU{z&*cWsZlo)ItHw8E&K-2h%s}LQPgyFlu?*O@|{BqUhdUj)kmUUW*ZAB'
    'l>_Qqr`wjD;aiPItaYpn{EtVc|3RXV^##%8l!-TjrrD1()Aw~<f3$F-u6Cg_wf8QflFCoc6x=^tF9+vnI~#~wIm-x_c~y9Khnv|b'
    '(l#BDwGDcgP4gSr|GnqAGr$c2mn-MWiC*J#lo9}_c)lAc!MWsb<&M8burNp)=>mIz^z;!nR3{OI(?4pC{bSKBm}g22_o;S<M9g=Q'
    'xU9%S3*>9d>lL=cgS`PuuMtWC`%e*td92nd7`65z=oQ&&6Rm4PhYpzWAl<QLKg33zxw%y}4R>tW=u<bg&Qk!CT?|Y`_l$Jq4YYxu'
    '&$1s7mo8hpR|{Aa705!!n6AqOd>c|I1I9HhVD-WJn7#$9-m?eP(K3cc&eM6d6jxBv+=_Y=Y038p3*OLDWQ}kPCn$(fBS2t~SaInM'
    'CoA%ls$f|&-pY-uTF!=Vd%w@fM{^zzIt>~vm~Z>pmtXItR^eSR&;*}EA)ezH5&E65nxL?8@Oxm{z{8Qpx>zXw$MS7gX3pyQ)XA#8'
    '3#bSxf#y}rTt^^s9Fq?eyN_qOk7v4%XS$DPx{qhNk7v4%XS$DPx{qhNk7v4%XS$DPx{qhNk7v4%XS$DPx{qg)&wV`8eLT~BJkxzV'
    '(|tUX@8^9y(|tVCztW<<k7v4%XS$DPx{qhNk7tslav#rhAJ1ez_wh{GeLT~BJkxzV(|tVCeLT~BJd+)W`*<eHdG6zx?&F#6<C*T`'
    'nX>zMru%rN`*^1Nc&7V!ru%rN`*^1Nc&2}1Jk!B}bZ!8Y4Txe;(`SEpys8$DFU#rUV)`zd-@-mIed3~hPEgI$t@5!W=q}fE(L>&0'
    'F9YD&Px;l=q8zR!<W5yBSEE}W>m*S}?+*5R`&oX4n=$HcVbx(A0g4F)#vRBY^CHQ~UA+5#Q7++>aX$4X23FG2f&IFeW+)TkNf=Ej'
    'sB2@@7d)8}YU9O>1E}!FaE3uwaLSv?3jJkOtT2@7^)(0wFqWu=#$^x3?FwdRQeM)L0JhcYCZ9~;R7qC4VljqsSmmU+JD)zx-n`+V'
    '8B~+mvU>A|w_1R~L1NT2MR!$*ievJOFID-ofkH?FlvPDtD`@3Q$I-2l`wR#X1n<E)olQyC%h0ApNg-dfc!rAt)gnl}RGEUp9Fo{V'
    '@IS&>Gaf`ge-a!cO8nt!fqb!;pv4+FCv*s~#+`HoBPM}yFu_cF6#Oxk(6aHk9G3Ycq84^hb!>B<FQB_H$Q8`YPenn|C*>0TN}(nU'
    '`V30Gh2!ZI5ijtpvLbJz%bT(y0?HT55@#q5qI>h^Ewl^r08o1gV~nC5%+_xn-}dtK+0)~}56@3dPBXGozc@Pm>G<{F<<aTUi&r`{'
    '%m-n$4!-DM6xALGTc6_}kg|SRkR5KX_cd*Avn&2}&`v~lwVtT@Ur_yP7&qF{$*!Z}ebr7xjJ3Yp^AHa9EQGz@=N7`30fLQgYwaHd'
    'F#B;wzM_tl(;{CmVhWCrg@d68Af7OY(0K-kKc48?5)9YURi7NBI*}Sj7joCySA(#Ba1eER4fZZTuXV7e`~O8V@~U|ob=TV8tIb4c'
    ')%8L@XmgaFSD~YnF2Q%?lk6h!@aW?<8Ee>Zp?Z<qi0mlzmSleo&hCBiHeW6msdklpeNbKJ^P+_ZltXkE5r64Jc0K?W0!!Te%KkT<'
    ')#Q}k&br_7bHUF!op`?~9X%KXdTdH$2N|-4{v~SQR5g^&9<Hf{1XHg^hCF;}A{;G>v#Z9MYyw<Yb$@Sd<vp=sHiD3qV$VG^Bgp4z'
    'E>O2Z4-&@Z`e5Q`I$OZjS^k4u5_sqyGmILhs_3KaYryqkm|XR)OE%Q(;X@y9nU}En2dCrK7@c!4rg`c`aU{F!Blh(Vi%;a<;x+Ru'
    '717?-VpmQgOs@q)$ATr1ADV&miTjlC#%(CMp}BqYm(^@pu-Rf-sCa`3Y+e&{>c-P@Co6tgm9Ud8%GHf5i4O0#uq{o8?mHWiKu*0x'
    'wGhAI@7|)Nv_EDGVh>?{87Ltj_KikC3(O!tl_1*Ty3<I&OpzYpv0LC8Tj>D(qmFdW^MEQoQlK9?Ad!(%fmGN5Ie5G~F=6>bgfaE&'
    'UYG%kd!a{mn_hG`_d<gV<K0b6d94?IJ%4B^0YlWkAeN5UXM>dLj=0NefX7K^qXrtjoXsYO2B5;QZtAvLY&C{;<F|d;Yz4O^_Al^A'
    'Z>ZDLrSF9Z*C+t<At>}mZwWql^TVw_oA3mU@*6mJz}eoVXW-L1E5m@fkt7Zbqvy_2bRw`B8OCrxK_{MNIMFa-T|CSnD2!}flqgjS'
    'LSCwVn6)G|gD``x{F{$K&}AIBPd!TPP>54~#d0&k5{3O376P@EFD4~ab;><BNTD@`dNdO^G7jo;9$9~^toh5R`K$5<I8{C^W~)lh'
    'u{}Mg#=vE%s@apUt6d2tatM7yBL@N-q>^@h;wr&sZ`Z^Cd(Mm5yPlDhM8uSIdb8%PTUUWgVjce~86PX2by1y!2OU=s;uz@mu-jB$'
    '@i*}yLfKGsueLrDmCK|MMuFgP>kde5-|N(|V7t|x*(gv2vxpkn1{U!6nzNB67ynXk`?g<Q-MEn|^RZJhw`@GO&n=NkO3;p^V5jjR'
    'G1%IS8BVV%ma?fg877;HYolyLi&8xDfYhKO_Zl+XI@ciE2}f;_{gGYBt<8Z!hjCmKw9JxPFjOOuWRxL4*XoYo6YiuUc5X6ijtT?j'
    'NxM=YXL42uE{UuMM7Sj@5+>FV;b$;4%h5Q}u+#@kxvveJA7)q^t)}gzlXb;%Y>9{8MiK4Jo~CIBQ_Vs7mG#v2$ToOuySXzRYxLa1'
    '9f~Ay3?cwFs-qTs?SMc~xY~)<M}sByZieK5Ut8RQF|;P=_H0^wAWulD+pZ4<(<zUl@sndH7fG$KR+||lDd`bScO%5~o_4XJA2Obg'
    'q=lrIx$amZD~<c`5&ybl$(rR!>SUwDW$T(&EpJ+)%L21bEhX6b!4({ca9%T3)F35b)8UaIT8z|l@6${vHG(=?^}TLA)Z1-?{ZNR{'
    'nc(8{rAPhD;~mF=%ogPpg&s!SLJbpP8a24OX+>0M2*p7)EF~2jtufSN8Kdc0T8iPi*1U2*1-&*c)I@?*|IkmO-^flxeqnpCCKmtQ'
    'kSG_dn;PC1fZC#%=j9?~PkSZ-pxrU15x^p>CKfXc7nfk955=ephZ@-Qal^pOY1|h29sMe0tyI$a-F&rRwpOwQx+;)wRmXclq|;d4'
    'AvJ_Mfvxo|YwI9-C-*+X?M4LOZDru#&#1eH+2qVR5f6oq*e~H{fJUX|xa(aRTqrYzD4;bRS2nwU>2hsy4!tnq^_amk8+Y<l9do<?'
    'ass?H&SA;SMJ_Fqu3h(&Gt_OH<@7~_??u4;8=bw0g)H5&;oWLgczd87au-f?JHUag`d{NL%;tmH6nMmPc-=Q4oV*ZTlc6vh=Ri4_'
    'cB7n(9s`K!vOAl0X_djm%%H?2Dhc2xuPe3m{Hgb7smyS20_6iFcl7&be?f!H3G2IXAJ1rzN=y>AB!@zLL1*TXi!682Bbn;BXX3U>'
    'K>t{wK=`i2L#JNz&J~bCxE$ULk;7BSqJ*3eFnYoJxT}Mz1&+B|P4n@XZR*?wOh>YUu~-c;kfwgT)kAN0Fa5@QCojcm`{UjrP&6FN'
    '@Sjhqeb&>n*>Uw_KkSKjqw>m8Nc|;_{q4Hfgm~k7R3qFnZKcpEKFmwnWdgAzN?qO#yel-mg~8z0Mp9_7bl<_zh^iI&^6p;7__-p*'
    'w@l+1!c*JgXW3C!&2tc=dAWe7mZL)<9<r7ts!y24hH$C@@>;q*gcc3jXotDYdXqcXPWH)i>Zx(LsH7IzO<5m=c`!u9G%AMddZ1uY'
    'Tmex2YqaX}a$-1mJf@bj9F6P4Ns&*vpP2HnL<KrE|7Q)2MA-KztG;=IWr2U;Ous9DgS~l!s(-Sp!ii0c?r@Zw!BLJ4`ILe*0IPrr'
    'O_!)GLo6=y;agNkAwRU4d>Z@`BiBP1q=1a`L`NKJ#R$MR^iIeCopJ__fV%sNbYf>hA%u^n&Y^67p?$Tw1KNRh074zJEo4?1a@90N'
    'J>fSsvPs`MyFV%URvdS=!ySH{Z$0PMTjO9K)$v~T+))&nk?@*5?D4b7cYS-Gb^QEx9^wrR@GQ$D>Ls9Of%YTZN;*bz#iUm*ko8^R'
    'vM<GC#+lE6#v8;Q9zx`0EOKEaOavjytfmJg6_+pg%xCkKU`>|PdO=O5X_ns<ai2~ofVy_3VUYP0AUqc>^MyTuNYAKF-32<H{NSHk'
    '6AD!;UJ7||v7x)s{<&K}0qp}cg(B|X;2!hH$PmdSJtFS(H;UdI(Z#e-2Sf*DB^eTPP7YMxH`<U{VQVsp$1V~c)@5Z#j~{;0lj~64'
    'G<jCK*^x@O>G$?aBdHH;>39>S$@SqTW=+S7TDXR08lETM?&(+v{_ZBY2iGsBj@wDLJf%H$NJjbe+~ciNig<aDPsCK&JI5=GLOB;_'
    'cK+bIpPxPdeqge(ynKH2*VpOfBMphqI1D9udaohToI)j&3@uSMHwq5qyf9m1#6#}RkF`{T`0?CPgpX8-z}XHX4(RDCsu#&D>Gg)O'
    'E6@H?<I9@*^${ht&~#aIWJwkFS%GvddycqB)le~)v<2WZnj94nx+hy_EIqA{+laC*R`Fpz0c~S!2Y#F<Z)30}7nRe|I-Q#<5*<_Z'
    'Pg~G#5Ph=!x6DJUa5kR9?+%{yNWL8u)8TAXC`F#S1_4d*=vIr~memp&+7%pHs2)dR@fm73nN@JQpUh@+f1=r4kw>MF3=5eeDfX0|'
    'a;3m1U*<y)r_p&<3iwA-WO>U@rTq42dh7f)Da+TZOx;W1(oebHJ_nV1;1f}~2PPYpduUTq#rGG;RRg|FzGT4ttY2O5-O;P#0Xcyr'
    'ok<VANO*`oNnI20<z9myC%SP)xFg)X*x^z=aZZ%`U)Jv}KsUxzcMi!%l)M*T{dn?npk}~#>${_$j>Wmuja%q!aH4$q>_7kWXn;_p'
    'Xt=*Y=L)OU`|kATzdrqO@am;F($?FEQ;dbWe?L0?>)_Svlhb3VDl->Kpr6ju)8nHT8naryvT(sgtyjmd2TzZFaPU3#DgWCSCnv9e'
    'e0IFK0p)Odbo%1>^wogfZXE8rC0Y}wQ%;BHCNBH6S7<nWsdr&L#O2xHjB(_b_y3MF>jHS)O@U^|n*r?k<ML|7TTsjVq8^a165#I;'
    'Mt=2<3{`mGLu^bP3M-qvpFS<HAm)*JCN;?O_<$37A6TqW9=^;cI0jBIlvdDI^*L{7=MOOd^6=Ie0gzcP2jhZLc2y)V9f|-1XycbN'
    '8hi58a5?Dw7B1}9Wp`7_prSX*=)BhA(VQahcS(PTQk{e>TRAT&fQ<R|;3NM1)F9n(mdsj)%%<#=iOiJg?3u|vIkd3A;3NKRKuga~'
    'lwh;7Wms+<Ek<}PVv_mzBmcVwxsY(vvX$m+n}S4h#!b^_optk9c6(#G&7JdXnzgJ>2M-^9WPf?>;7$tzA9v#PiBA3WsbfHl>G(>m'
    '4+!2TWW1X|`g~UjpkDrUV4OCvS>M(+)m7fa1`wN4ELwON@p~I!DLC>b%xC?+oa!1D&#1Toqz7=67>x2;kpVptSfo0ngE6wh3jy*_'
    '{)HOkD&BDuiMs=DTKt3zRt`87&5$q4TSCBbZ1>i^9MV1zy*BX?C>X9`)+}m26(3Z<p$j-<+}{pU4obwM)qGM8DKqmm<?3a&S{aWl'
    'u7z8@TXsJAv0K1EI!=`HX;g-9>Aa^0A$#nWq3ONaE(DEu5|o;mTSU-Cf~1+p!kx?{t{`8tIl0baQfKkDa!|CXNb#qrYp!%H6+e!P'
    'VKUt7hpJUCutZbpLM(K$q^JaK;-!;2Sb3~>e8&2~P|Sv5kD6$kx@M^MH@4g&<PbcH8={LkP|x<|*}j_J1i{$&6IXy#F6QX4aq!I$'
    'JgoQ1FkG(B{NR81^I{8xyMGi@=SoM<vRCe$`wEY_f(IVIX<1rk;M%y!%PFQqqj^wo*jQ<bdbSbx0@NTsPF~o(UhhKj49S|SRz3i`'
    '&`UM&oR~XsDd$rbB3{;(V?W}iLLjv^z7kLLruUc&sqtM=jFN4-j*j6;u7udCn2gtPL_%n_tZU+&+1c$Q2&l(?Epb5@)2JLgsTYf;'
    'KdKVFtyeFrfm&=)-Q<EyVCon<Gf=zZau4yj%hFU8Oa0Vrw4W?rbR61n-)M2dIHMd$<oXf+eqybe9^gRAignj6j#|$zR9iy%Zi}in'
    'XqQHh9ptHOr!MdbP`^Ufz>OEv2FNaes18A8VD;65;>UBk22`nbjAkOqs3}f|&txUoG7@b!%yO}A+<g+;jiU{mWDsQ5Mu1R^6OL;M'
    'H<Vrje?H#|zHqG_8evMs8xlp9uE?~}qCR11hj_b#nipsxJe1aIwjU>*i;={Ov`Wx6BDG7|K43dV>Nq0f@R3pd<j)0R02q1dIiCzn'
    'H)ZPtFhP!HW$}PC!02Nj`kT5&M91|ecT}HA&}m4-d${i3BjSYiZcybL-5YL7lAd=@An0>kJClC6IV4K7-uD-W2-c>)Z`=aBV8fVc'
    'qZt_={IE?t6Y7*~(WOviJ%UMcB<hiGOp+*0T+vL$?pt0osu!i5RP5e(lj`TDireP4Rk`^@=(9NsznFd>Tf^RBbM`oqA`WvP*`%g>'
    '1%+cJ9rxgK7vpB+?{(m?;LBq1Jr9Ts#KGrQG>;GqOL9j|;#LO=wc-Jl)-H9dg3>N?g*8rlKQej3IQ8Mbj%GJTQ0j}z;8**9!qk6}'
    'fX3^s&;J-8h<Bg=QO}7G`t&z?DpE<GE_8DmO_7T<zDAztH|rDJhxio3iNv*f*VkcQBd@;s6_qq}-8a9Yk`bx(qu=^M6!kq8fBKPh'
    '?NtW#%bwjw$$3f@)!HWfGIg(B9XXb)elN^Y*Ceb*3zla;*1_ZEq{r3m2epD;U@&A`jDFkh3F{}WzTs-txOa4N`~9#%=-Z;xR;FzX'
    'c*Y>KVAg(xIi5HM(e0`WjQNH`q6-`6Y*$Y>>ri*OD6g(C3J1B(bm}uEVd!`qJ&tyYJR7f|1#+qM?e{R)+&S4-=$VdLsF>GPS$;kZ'
    'mu}DI#guL6=vaFR)Bfj>VajE?SY1}P72PaR5&BRMMiTSaW$&*slNP3T;_&d1Q{|CUkc-o$zEN6fP7noXQ+T}gU%o@iq%CaoCXrIY'
    'Q2&CjA`d}4v5SH$=#GXRdn)~%vNJ^)iuUf1pDE6hw0DOLO%aSQ_wJaZDM~oBZy;@%rD@NkY1-R0PgC=VZkefRZ6CJF)nvM$QP?qC'
    'Q{qXSujzM8iqxDh=sp|L|0mgyuuH!--_d<uqWio=zhzz`PQO!d%ylCXhTDSzO|l(?UZR=9m^Y6}bVK8P7mxR(Ou%Fa(^bg61#c;d'
    'NIp^NLZgHeT*F5r#YtI0dK6JSC2v2_xB9k?HqYfwNn}llL2G;-^|@wv^I3M{5^Bn2@1t44S<ds(DEn{wS(W4E70a1VcHp(rhOIG1'
    '-`0XJRPvVCK|!!mD2LgVWAAKAwzpPnK#xpWk&#BtYRb^O!OZ+`U^D*p21<^IJ>|2D^EkV?DMlE$IFOkWfkM<%CW*LtHM_*T)a5(-'
    'lv7O&?0Pk?%+gg(bBxshDRVHqo+0gXJ?BRe*nw7XMoq~(I61R-NNCErQ(*pu>Fm9E=4`a``+Bx0|AAEMjk5A$1I0Fac&IBE>F#UN'
    '!60-ez4g&kq7#kzsH{lEqznDYdF%d0ZXqd>5T=P!PWiwbg%H<(Bkii<u^)Apv#vW3I~|-)JkGFQ@m=4T57;J79?r-CoTFL0>=-V?'
    'gy+aC`<@s1vb>QHQyCr14&=Do6i&G$ubLFZ7|zY7^$<<_0TZa>`mc&*BEq|_K8>I3s^N5WmesCwcW>}EcOBhqNY-D0<43<^_M6&9'
    '*{Q9Ej>o}o$Zn4MYZ^wKsjWw(h8!E}t!3eA--9WtXkV#ser9#q9Z*yS%4$IBTg<0J@YLp{cc36qcuBZ%#kHd(FS^P9p7uIQC7n^S'
    'P(KWixrB3bGqINq$7<1CD5$8}<l53qiwT>ab=tA-6IWj1hb<BsbF#o}fW5W1&zb>^w>r-fcMy^6)|K_^d=+Hgup}NvjhH>wa7mpP'
    'Gu}M=thV&e&1KI9At`Ae8pW>LUu!U7IoN8dR=ofA13Rb{a!bDNN1=Yl^kq@Wp6p6TyE4V6CO6vm<#KpE7|yC?YL|QX@a=mz#Z+!1'
    'Qt~^=eDuwX`-K(iUvc)IkiNtxh(yLiH$7bAF$q}KyHb)Xkm~Td@M_Xpj@>~z%cObb7>K!`Q7-EaV;t$Vbz+QKW9#1Gn)`fHfrF?('
    '>xrBV6<d$sd@`qL$$qDh4pW+v%-jyq_g(N48o4{@dtSqcaT#YME+(9fg~vS959Jl&>H^MyV{~f8?wt9%XM27r*;3sM_X=}2a=#x9'
    'F0m?c`UnKwjxBRtylKo=>PBOqFp1eSvKxU8VIEdrZ5Ja0x4%K#%ewy2q0@zH$2KPu$2V}VD;x{kNs+iA(eBgPRN??Z7(<t0xl@Po'
    'mT*U~XDS)5wW^p^xtuLY9*fes>rR_pw~g%4l98?!kAbb5nj1!dJ!20(51=A3CRmU--^Kv7Bl+T1nUV0u6qD=)nUr*$QUotKvk@AS'
    'Tz0cxm(=XeagUwsY0kF|`IZ}RjB(X;y3CHto2V@^&a&ky)b|#feRh*ICpeyUjC)ZhBRylIPl%X%j$W}*C*&7XQN7B43Lal*=NbI1'
    '0|aW>M?+v2?qv4~XLnCHTfxo^OppD~29siXwY+Xoz9r-8OA#0N^Wq}XOG^NlRH^CE_sp)x*<q<@e5EC05LAAW=!Jufry1sGcu2`u'
    'tvMi{x|u~GUd57!`Yzjo#D&Lhc+u6}f=5l;#?O_>NX}>Z=)YDK?HeI^ZRGwViQMza{5lr_t;WyY#rI8_aQ$F&K{R)S+!5<@fm02q'
    'eqoQY*hMfxd1Jot?J|VNT3c!^?VYQ$YC9)2r+W1J5!X+64a=_5^L1gzi8FcEb6|_E?1S6`91gU$a#zrD)G)-mz;3bainIe%{jpR>'
    'D>Wl1<yRmVPlvano1lAuEQrSdzPA?%DKy6qGck}w8#2*R8<TVka1#*A=}bv#q{OpMbh&hrop3ynto5|_MO}q2d`Oj0xuRWvxQH3A'
    'Y`(Z*kWWPFmMxcl+GTHZH)i?VAnDB0zeVC{eY^Ws`Jz)-4L2+`8OtcN)h+5sX5O83=vk--Lh85n(pDmHN=UPot>DKb_JhIlx5JB+'
    'u{IHRU{5Y__O?m0w@8@H$*q$~v#WI*CTF^qtk`$WbKS6QqPGz*GT|m=@oQIFUG6uriK#RG!586_59|e`zMFy9uv2aKc9>V!16g^d'
    '{<@X?ogDXHynNc7lyBvBKhOJ_eCc9enii)NQ<rd5UOW9iT`hOz9jcDuXmVX%mgHE4XV!TM2Y@b51Puep?VPqAdjK;iN0svGn$j<#'
    'qt~1?LQBzm=eMYTM)f(%(k>ff>Abj*A$|Ar-yi?@?DRO9fpingDYwo$AZd!y>cZ55*ujU}rRo00&iq>Vvh~XSjHztZ9yZEVJQ3z9'
    'nLmW9WKxSpKqrI{+s&P%kg;t1F3Lm)6QkqBH<r5BHqF#Gigto@FLq`B4BGL{n7;}Sh<1o(5eq+S^klKDMVtrC3sTH#y_ERngMY#?'
    '-f(`=j<{PI8nu$T2YrHNpVz#QcaZ=iSk`XRr=RN-b^UcZzm%stehmNZn_p2$Yl`W+akYNy_z{0`E|ByZS8TnnzH2p>p+c{~`?h8$'
    'iRkalty6c~jH`OFZqF1TYxh2{5ucR5tcarm-%~f0G@i#BIqF^b-XG!{!V{}~*ASX(T0Wbcts}v6*Gr7Hzr)B~l%i!;no6zdrS&ZC'
    ')|O)tZ;_mSDqR&xzQHj@@-rv==jz;QtxbsMZp}?e=5*)!=fzBh{m?q?kebDkv3c*=-}<XplF}hcl>0`aBwhC5{@z8i?Ds#EK94;;'
    'PEnijoHdY+;Mb{7+_8#OL@LN!JlO{-irp8@1_L>imdn9_<Ejs1zJT$xeA%JQIfp05dKp46aW9I?FztYF8u*VIu)ZM0wVP5OsfKZP'
    'rk|#J8?XV1i7IEK8TEx4A?@`7o#7VbHP0FBoLc5VTMw7yVaA3X-<vHCy`uH(jP$PX=K_@q3!@U^;*#VT^UCWHpbYc+fr`ZT>7%7y'
    'cb`gk_k9X>haRQvP6#|Ep;o|$MD;BrFnz5ZII5mbmjqlT^!EMY+|vo`br>?Ahg*-4tq_6BT%zp;Og0fuXrFkuo9t$BGH%D!UAth`'
    '_mlucG)=3guR)&0m7~~gr~6TxBvqu#Jvb9O9<J$`T;$Q#lton4Gvph7)V4_~tt=@VJrhhQFX3o2!*NNZkL2YgiSp5e0*i{xBEP#0'
    'rDh@7AJBjdZi*XB3LqENNJYuZ>8{AB8CTS8Ag)S$ONg?JSZh;gBi6WWGNx=}GTGo>_>!mVDOD6&bx4QY*P;dZ+U;g?3LP}*^bWpI'
    '-UxV!$$%$+Ak@+F$*~#ZLyHH%Fuz0ob;()kW2Y$m%6SH`n;UZX<@*_`1eor|&>gzGfDiXxk?=5kPTBL~cy@L}gIQ$<wXRsqP<ZI#'
    'wD2JhcDSB{^YS$NZ2!rhK93>s@N}J;w(Hb%X;=)6qyUlT-8~In!g}%YDXBY*S6+Tuq2}bWpc_%K|D{Ve13m9v0a?$X&Fk4@1h8Q*'
    'EJwVt-@p*PE3)?`F1MQcg1pW9^~-KF15k^im9ml9sM>UiP7NSmm&0S(s}Z9$#_xJJ3nxs}7o+L7fwCJ5)UQwr`N!~|&71d58~5&;'
    '_O2WDoi^(&?!wr#J^NcQkkDH8a*I3W2$1e<=U``Z&qwo~N@~bj@xDx0FU<u*m4t(yZqgFsy7v5aw>&b@b#pcQjQf}yKO<v+#<(Bh'
    't;TZOTk2xlb1<N$t<v0)#9ehPd8|pB%>`r^5sL6rV$ND3me^frw8|#~p((c&$+G3?aQjlc(b?x)Zd#}gkKEr-ilWe!5D4sdFYoC#'
    'ivmH+<f&V&iy)R|*L3==GP*;kfST{h#cYb2^R6rha=FX#IE~Do8k^3_%H<<3m$2P*>G~W=R+PE@aaGBEU~s~jp~{`ogTooL%QBg}'
    '*|!T5m8*m6pZUfykkeK$hNG}e3Pv8TTw;cIAHC13>;_J#@az)y%FJDsWVW(kAaI)+Ap6~Hd5x2wmwc;Pg<TPuQ&cP{G9-37o_pj('
    'DN)7lT9!`QZe_J2g4qsOjlN=d(G8!{I9>{+Z}oIQ!t=ZBHUB)WE10Lapyv}(cKvxQ!C@O<3tTRg2D%eZlGbFR(TvQgnN^X{-%u)y'
    ')ZO?SAG<zxn(&+atv-9<&621TE2eZ%AhSjn&xOc?x)dJ36}wQ;-+I54)CXdJTZTw9Ng_bu87O(v!tK#5_jsim2C5+^d-LYIpa1S6'
    'vEIBnpNd(;c|(KHdRdHTB*?N37|r`b&S)gw8e}Y*;?fmC_{|%XngcZS#p64~$-)O%98Yn6#Q2BdE0gkuOoA9QhlU=QlkrkcoBr<V'
    '^C@;mSQz){j}_@z#U#l#oK6OFE-n~&qHyhW2-BRyRp3;G#zi;?`CJgdcCW6N-YJ2iYKG*>&dD5rvjL0XK_RB>FTcnq=TpjBkX18i'
    '1f3u#l><%$-aHJrQ%ugZTFK>(4tc^a#PpDD^JYf5DB#;H-1yMtd+MOum^1dK5S;N6h)J<@j2Y@s&I~Mkj@M5*$BTTjDDu&5m+5sB'
    '+(j=*2RNIWiyWaMoPx^nty~%jr(51WsAJc7%N<m3NtYdA@?@icbB8<?yD9}XC9NQB-!qIjO?p`-?x7t{fbcMSVabcU*|Snd2kqul'
    'Y2qHqk&@*e$-DjZ<dx*|_c{6{$Ajedmn;}Qt^XH$xPd%91*pERY??lc#(ua1A|%F8_e_LL7hg19OR<-@mf~x<LE`z*U%z*)V_F7I'
    '$iOK(_S!o{PQE~nXw)0U6lZUANLQ!;c&sGG73V;m^+R9z72Y9<9!9(%my3K9*kyLJB9W+^Oi=5vBpENPVwV~oSEWcF_;s+RHM%;;'
    'I$(Uc=U&a`Kmd5rnSTG({+G_0^kHy`Jkz~#6`gS(aVGb4Ky_RyACUc?FNw<Y!Oj&Nl@FHJz#&jHQw}0gS?G3=za2O=ybp%_+9JEo'
    '+e8f|`oATL^;FO|GxLF1WBsst^BzheXc@U&jmMb8S9S7>VALC21H)U)W;Y(dUKn=lu~nFT9$tzkfV|k>Q!rsC$%ifyhhFY&Mc}6>'
    '(Z2@XgXaz*?kG|hA6>3)wYQIxrzewS^l*B%!#HxvRN6yftaLl!EpP6`$yCJfrrz-MeTQ^0!o<TecDQjHEQls(i#3mt5Ng=+teeMv'
    'hw)G2L<Z2U-yx5I%T%C5qYS4dL)WN9IP_ug1*Sb9q9o0rj(Noj|I}m#WG~P<JwT|Q&A>zkTK8x2N=RiIplHwm94zM~A8&{xPlk}E'
    'V%j)Tv!GmqEL)mTnA9Q?r?nM2mA(f7kD^~t<eF*`Rc^v|z6&T*+v~K=%%z=gYVm0_IDU1hpkYUpYUlzfN^Q07pk{#5)lJsN!<)Wc'
    '8i+w0k(dr%R?XE=k;yir+tQRK{xu2L8pp3BhLU2pObWWdxul5v(xoCcW(&fA#84Bgt?$1j%c<V?^+<U2v<b&l#N7~-xfOvo6SM3y'
    'v}>l8!8W^ja!p7M0<$zuCCm!dESP8yRYJj=bGelGT){^UKkwA3^X2rpb<Y+D6?HyOasxjN4ZdRQV`w)~UV4Q4^+##1syK9#x$eHn'
    '7!Xepg}yn48k{CM5axX%3<l@IZ{a!w6N`6rq$OUll;PuEH0PbHi%(<TBMr37Qj09o%FZ1_#W-<ZWeudJMv5G!Lr>IV3AqYTkXoB`'
    'x)YX66iK9a-gjkH;&D>z7U=vb46PD<z!DG1H~@c?Oc^$$aTlw~)`^*2PGg_t`tB)>ZS>@RaHG0oj^oA@#k)1M-JNF*d6m_zPP?U7'
    'j^lpz{JN4{4$<gYk2RfkD9$#7pY<7smYh$x9i<(T_Q{j3IfIbG`q6gTi5$#Y-U(8<NOx<qXgi#^z=kfFOQtu9)Tjw77f+tcJz*xb'
    '3E+<TClXndIQL?aFFnhMc!Jc~m%H@VTT|6I?<x4G^R)1lbE;TsJrYg^-!+rHAj-+)*>p-=7oevT$A|837u7nP%}d%feq~fE!-+29'
    'rEc;YccYrT<zB|It{#ZGe^*HX1Wxq5rndFAw=D`NJFFK`d&Yw^G_w|PFmN(t>)pvk^-YX?RURpO<9irugjua_bdr+v4c53^=;Ghh'
    'C4-S9vd!g;wuZW!v9>P{NK=syF-DOt;;vekvwQ(NRQZo0oP?`lc@~|9-EsIjpNuV24*=Sf>f*o*i1OxWQQa=?Htw62-Rbq3SD|J@'
    't;7{_gJu4<Xek-oCbd(tM@k_OW*5OsC1x|Uojd_{lJ8To4gMxW>kET78DevaACtkOzY!3O5Y;q$0@bZY2Y5J~;FBy}W96Ee*bze0'
    '^VwXQCgY=-aKXUOfF#lwhzGqK%qX{Z2#{k*P&7M%=S2~5bv2t!VG~cT_p%NTqf9n0895&qumoYh8e=dN370o;2tuK9#<mz-w=Z7c'
    '$!Jktu8bM~h;oJdd&*fTb>=a#TeI%4mt{XsDSD2a1SS;QCguiNV#Q>RL7qzvW^;+zGGvIDJM!hTr$7DtGRv#%J*o)c-|tUPUOs;L'
    '{OIX1XWwCCk~n#?t{XW6+A=5E568#fJ4^wYAM*t&*r0n{5ZW|;X=E^56r<9gAYeGibXbrLpKVCeQ|>rzHSe#>;WZp&@J4hROjmTM'
    'a+D;@_;-uZP;3TeHzdyXVQPWaE)PvdQP9m2J7(FBVmrzrItxd6iFU+u1Fk{I)0lBT>a(v<PJ>vZx~uw;5^!7)3L236L8uA=_oeeX'
    'KBHTj;Jp)=Bw+^hc<%xv?1wE~AaO^jyKfFH-u;w-)b^ZXws1}u*f5sVk`1&akDQz$pgE)z#WL0Fwn%EeFDAw!lye~~FzT{EaAVcN'
    'qU&3I>vk$XzlRbdo|0rxNtBH1oa7}~yNA1xV3`F-3=SN4Cq-s&0SEc(_0M=kdUO%Ed9LmPe|mx!nR|Z}6)lfC?m@__5n|@eWW<q3'
    'bb->h{b+bI2iCpPld&-vsebdc!i_hBwo8$r-fV>HZT|g0)n|Mw)Vju9*;*DBV#J}_aa?>F2^eW-9&i=UXz`dQCRkKZYVBbx*R9a9'
    '&=u|y^!$T<es+6NyW^~m3dxszK{nPnGsBQbu>q4;8!m5Gl~`9bAK0yPE5fMKcs|D6PEN)x9G5mHbiwtIxS*}hFKJl@VMZ8b>NYks'
    '5n4^Z5kV+nCkXr$a_7_6B;ra&1x*nv`D{wkh~Iap&2(srhtd>`0%&+?t`^ptJqiHo^*<wz5pTW1A<i&aBk+|fL$~+w1P&rF3)iG%'
    '%ctU_M_v^!t*gOzy|Cy$fxOnuI7>VYb50MDh7}RDNd*zhuOYTt)0<f|_*weEJwpq{FDsUlco}LC2N!Lp<cX1Zl1#aYSz_j}HecV)'
    'ImWG{;@y&zs9KNmdAPF)pLKBFU1+3`nXj9=Gd((K)TYl9RKvmJQGDdsVOCLKl}Y_A=g;qYXg!NJLXUlYEL!zp2%t)KoeSD-{h_?E'
    '$+LdCtUCAOeUPY%==Vco=}JLI-~u`kj4hiYo#+hg<8TwW)tS8;8eVhKZj#qF*Z&t=Prn7z*9^a5{M9}X7O1fQR7#&_-hWrVpIW7#'
    'WykETzTbOt(EADxZL<lS5BZ$s7jWece8cNvNG_+CgJDr!mvh)eG&puR&&d+abf0A>yo<n(?#*h+8CU{n9P{C1MHTR@+R@<HJ!?Aa'
    '&gLStQv-lpS9Swde=RZ4lAK4$0%Px1U<n3U(DRe0KjBrZjY5y97l&q8cJ>2Z>S~K@%NU~dom|^k1{YwgIUHj!$4qYP{2_<cq3I_k'
    '{u(uUpEYI)R-4J2i8=@>EqZy`BC#%|FUvdGB^skUZlN~&un-LEz#_FTJ6R6YdudS06$%_WgFXOGlY|crNx+L#N4Of;6UN=)B)XOo'
    'D4d5cdE0=$z1Lh)0F~6G^$AUsToaY{B{E4`$@2!Mb~Wcf5==w%82u(Qb}wF3{-Tun#V8`<bHBp?x?GExBTn_OljxTWTqKXX{60Y?'
    '84){TnaW-iEfKLK2W4?Ibd<G@NJ*htOZTGQp_#oY`-<;V-L7Bn0Qzs?D4R|cAC`+e@cugFl-pE4^IooJ1b{3(42lm|{(ajUqoQHc'
    'J~EqT42FP8qEgr9SrgO8H`$Y4Lko7h-Y(nF*88slw-;7smdtpRp0roT5yO^A@Q%)Q_j?$pcbufbvX^xVu=2mY8)&gCr(n~{2$>uM'
    'mujcL8;!j4A#~occc3Jjz7A6=DHmJKR#OW4>QH4di52zM@!2M{GmcPe*mBHaX+LSqd@X*b66=7-^SKqakm?%U>(Q<EF~umnhb;#V'
    'vluIf7l~4CIM#3*-rAtqln|5X(&+fkY}fz9&Dolp1pr?C8Q#`iQUVWP{g|$pnBIh<(dG2^WJB@2jEd@+o5tB(G#1!eh;CE;d!*Td'
    '%&-@S$1V^#webfaZ2~!)Yer$+5A@X+;!p60zQ;WhaqIv`(!J`h@nrCE%q}x9HhrP8>gf@%7IfFsU~U#*qKUUwXEi4^sT0+NX3gpe'
    'uZugTU%~d>slN^DtRKE6%BjZt8j*U*I=S^z`>zJ97IZ)Q9o2{xGDNhG`ZPj@+tC}H?UtCp;L>@Y@5;au?rHkPVLck9W4VGdUZ!t-'
    'YVeP5U^X1@<~;KBat|pF4Tspp!R`M-#xf$d*uOnW3nqd1>Fi*3be(6r6DyT}yMbbx_1wsX>xj4^Rl;Lv)t`n;o%J2?0GiOJ0&8$r'
    '0Bn2h5WeczlfI+F(41kA_ElPWMLev=?Z_&yk>yFpoW6KqG$b-gp{1nTA69uPHIQ;-Hmt5Cz<?o5l`!ZO<1t@0Qp3mkZ6J2Z<~q)='
    'CEYRW=csN7p<{CRZ7slCct8k`Qe4oa3Z{jv5$QMdw9|m#`)l@Ui!SF7>yhaP?N*8)Ez3Y{l67%v^l?eRh^_A00-YQ^)1A+<W0OC8'
    'IJ>ziNmi|Z@sC!+!iDYmu-PnB0YO|GFdQ_@z@wcTG7O%bpg!r=IdF6^W|uPY0D~?klq7*8ci$JJb%%EjoOXwB@qy^Sm6QKgD`mBA'
    'mJGBc#A1a@Xb#}CJSXejp8h!hi#kuCuw>X=Du3^0!(UC0o2D>x2OPiXrVo$WmwXouZmgek@rMJNgqZ!%1=GW#oV4n`d~JP)v)&MN'
    'EMjy!4ZkmtL#QrW9J=ukgfp$KuKktqF^hnMC}5~@f9M!sjtkmzqK6w~VHqXfiTryv6zV)G15%5t4EvG_u<vg;MG`G1n4EqR&IEBr'
    'UO8Iyl`hF``L(c6qd-!kZ`g-5;7BrU^ixN2`7xi4o<f&iV7435n9^SFJ@|GTLK*`fDPLpHJ)N|QCBd$Rnu@PQ`-G5S7@6eNSFtGC'
    'idyT_U!D2OhivvYqtUS>NP{0mU@>m}8k%NY`u<xzCQDplXg_5x+KRTmn#ZRWeGh#S0CF9!X)zkz4U<<RCzQJ?UX<)7%9#)M1}~sU'
    'Dv3Bu)cLk;<tf(S?BGYj`8lXtnPqR1!T2>h&c?mNtHnBXg&+B`G-N!l?>XD2Ki_FfsVgR>qme={xmOwsoM2Tq#C7B7N<z{q4N+8x'
    'w1%BXLm6ZKTi7c%nh;Td4%y?CkBYJssdY(Po?VzWnz3mGHU@)j7kK;IQgu>}A_R9AmC%k|{l+xwU`7P%WV>d1tq-QUK#`!<DAWLL'
    '(rO#nkNOPC&`D5fds>NOcA0iqR&Pbhhi!>R__Vr}Y>OECd&1dBI0GMCz9FbwiKxGlo(55-fla~mx;Y`bC`&;tugo#!f3Z3KFhkFH'
    'HF3FN$b%hZq>68{!r?2YaB@Vc1$K8)rPc1NVvwA%T_tPpBvp{jN=B<njIxuDd%@#5otrf(9_1rLVy(5<iYrmdB9{XF<0s07`tj4J'
    's8mB9S02}7E?0hqnQ+Q=FK-9TOVR~CtbMhvs++Na#7vCVw__rqsZg(8jKtteRF5~naa;4+LYOOSZGmERRje%lWLGTkM7m~tB#+Mo'
    'Qw=qZzm!=!N26jsncb4uQC&9;jEkBdb24B$Cu}OKPIsGXxOjCU7nk7&ORLMZ@MF>{64a%?8X#ZF7UPYVaoi<-+=WFo68G71vDw6('
    'GUpFK)SIrQF`p9(-*;nYhw}%RXLnLg3*INwK&D0Rax<-+(wo_+NDq+jX;}Lz0dTI9#Mp)3oJrV8id<XGfMkEW&MTr+N`vbr#G8=g'
    '>`OE)=n7@rH%gzhS&WmaeR9fh1th>gv(K7b&G?c>l~yK+(Ztj}^N=q#TK#Gxf{3_#T))XAy@b0t%ZwDZViP-z)wD%cF8nxi6w+@e'
    'qTkxnM&nm%3D|oUlWBtM)@QExAzV0S_3|`JQ=a>t(=CLdh^W|VOWY@3Fb-z@DSobsrZ=?#Nx*d<;#Rzco)D@pi^Xf0Sr~%mO6g8E'
    'R7m*h;)n81rohyT$D?O%Mz4vojvT-3>vb2M8RK<tcC1tq*jkNvhgy?4Ha2qY7$!)~?{b|J4KJnGtZTQOijeI-dIlQp9a~z;@UxY*'
    'OgGwOGD}cM!gdxBz_vCtB9>^a-o=;}HSg6`o$PLAG?}-E+H2-CM-SVY)SA#tkw#FtT@`kK8p(r$<wnJ1iSCDW>xrergj&rfbqUTj'
    'OXnaQOAK_$AMA~)(RLHalqN@&a7Xd_D$qJS@i|Jtin_WLJg*QQsL(v=JGa%<y|8@~;j4MHw15_0hp6=?uo^<qP68?8C(4J5(5k{D'
    'sTM>VzEq0X?q};`&CwlR5+7yRvvD@h@%H6$uv7*(`T*-k5;M2YOZ4o?R&z2HqO<;cyphWxgnAZ#^J)M$on;fuD~~sXQvc#pF}XQY'
    'l2vkJ$BiOm*)IkqM~xomG1e5x?tOF+UtZ6uLR1-)Sr_mudK-3}#`E3<`xo&;GY@{!6IbF9;hb5bxu`pxxnl83#G)oqw64^!@yX=Y'
    'Z*{CQ8i)CX<un*!V>747_i2ppnr`jfrP@?9?D@%ZW|pj5Y+|Ui#Ei!&IZT8sWJWAb<|I=Ra{2(c^X)7Yi<_WMnK4Oc9Bo?|J`!)T'
    '!EG|Q>hu%EOoHJx5g`q9=F@J~bGg+nB3Z+%{dMH2<+GN=!ztnZi1BZG#Bc*|PZ};vpIT1q2Vw?`*Wsm*t6!hE>!~HlTxe+SW%_?7'
    'nO^e5@_lKIo(1(z#VkXS^>2rqp0gTLiuHR9kZqxEda9k?v>lg58*&(;U`cLV<R0ae+!U|Eno4}9mFQ9n^&36F-KS1QT8$UITF0E#'
    'z{RzU?`^+ErgoH^$6)XS+HSa%iD9Rq+R5pga5O7+d)IGWH|01D@KQ2s+Jia<wvExaR<9E+&RXlqIda*LnOUY}2fC*L?|iCr!F&vd'
    'vXQuVDd~A#j$vvIvk51|Lt@{+`Uo~B7FT3P4uLgiH4QA`v6g*XC)Y$gI<38kSL<=8%kO}YD)IX+0Dr56b*86TsSU#VJ2dLUsuc;w'
    '#u61JXZlogo7&OaDrWWWZ^}#Vk;7EmHDYO4DUE5j6KS<;skHGE=g01c>5WUKyWIEF)W|uh|7E4qn!8W^45@9Uci@-8GSsO%a?z?U'
    'LqxB);|aVby*3@h4e)w#ZA7eJ*}3lMp3>3P&qTW_I@ifaXNTSWi{{NWrqkFj!OXI=P{%X8c4cm&o!I=nSz)356{vL6bk$WIk%K{~'
    '9lvS@5}D!y2zMjHn!0HV{Y6shRP1XD5N&^R9r@R9H=*mC0PciT5>QN@4$q`tvO?F1%0cW@Qd~FQT+9^gy!AF5tV$qEg+_vQ(>@Uw'
    '>ju54PJP4lFXMeM!c4eyVh==_iU+_}!Ql1!Nkn~ZRQb_0FO3?%hD!*XXH`Pg=dbE*&O6D&n9LhauXa=xI`5L2??uGW>bE_|whZNt'
    '(#g8}wH$Y*CGQE7i~CEA(wPBR-&fqlVdz<A?#qkD166{q=r{dlsjGewSrY%V$lv8c###@ADd6m1>+|0?!rqIfp=n=nR3B3Kf16U%'
    'dTnk)`vz!Y4H6z3yIZf5Kqh^uTU56}=&fOzN>tUbwR-O}x3!uP-e{mpWViN<mMNS3W@z2<3(@a4UqJgSn#NClRX7)<ZViYQ&Saq_'
    'rl+JEf0MIh?x;&8H%pH7Hog`-bmm5H{pz#q`x)neQ&+$)iZ0zc;qJ|%3!9lYSMI*kUOYR=CY*y9PZ=3*%$&tW2OLus4D^1H&j<Pf'
    '-4+VCgZXSy4*d>L?d)YM4#54o!*DACX?(S~+3oIYrf$ofy}W%<HHCiaX5*%tj=4t9<IP{pJME?`?MAmDOF{1{ETs}R7<0+<>4Q)I'
    '2g=EHHU'
)
)).decode("utf-8"))

for _name, _source in _MODULES.items():
    _load(_name, _source)

from scripts.v19_terminal import apply_overlay, terminal_market, align_hands, _shed_access, _move_toward
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig

_V50_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
(
    'c%1E>OOGW-ZiWAf&}%LFEsb}r?i#5vEtSv@3u8eL1b7Ss#&{unXZXLn>v3;pM1JHsjEGyZ0WSpIuDX>O50XJ19x{IZuSfs#+wXt>'
    '+wYJ5;ftRi{rKv`heyAB`NgAu{q5iX`9E%cbn}nD|MvU8{p~+*{`K>tZ$AC?*B{?szxnj~<D<{N`sur?S2rJ?KK}g0pC5g=diQSs'
    '<0mg}e|+;tAFi(6G{5@gm;e6qi{|Y=T)+SLUH<y--oC$jbo)&A)6KhI{qXktSGNOuef`tTXyG>>zPq~m@%DFzaecV{)Q{`)QoVis'
    'mrp;Qo_YJgpRPW9y!&*XN%OJ$lXh;0w{G9Q8(R1N-E-A@zxnj`-J4%O@9oD=H>+a5_in4Y_jV7n=Kb!~>nnHKAO!sr?w|R?$7Ybh'
    'lDvLp%=z^7Xn|jSyn3I!<FHkvH75o5{_5TJ4=iYhwGGB|Qq$cs+&wk^S-+{y2th^98-X&3Z$6K8w~G6Zx2q`j=g&7I>t42d#_k;?'
    'imCkDQ@<0WZVa0Uq+7E4UbldQl0pJ&uReY8ZiUCCqI+OrqjtY0UA0e-^K<s^KAUdbp`Gp6jRyqM9|Y_R2?_1SVKmNeJge@8kP_OK'
    '{!dnJ5DJIbpu0aA9L3Sax$q8w_R<*geX;ad9qcr7T>kT?;~9A2RnKMMemKq;s;j<xi@WN0lCD_w!)pg#kw3Tpq+XD@g#B*B?zrdc'
    'W!|J1C!UJOu?IgK_C$8$JpI~y8u=94BTm0{A9nrj-PP-lzyA5^{l~ZO-u~0k*lrKx@45nq0a5hGv&Yl_BGBej47vOIjY&C0Y!H0H'
    '8F=;TC<!}X;NZoRNr5+I9&x<vY6aq9;99t*?X2Szvc=ZioOb%g<5EwVu-)S>Ja9A&E2gknwL8(g)C6`0Xu;VLnu%GZ$=~`a71QDK'
    'Z^b@d>TD*d`2V4K9!=4E`SOeBsRNT7Ko02WffoWY6K7-M<>oMj?_3>U_849!T@LYT%dufMv4@bHc*WWqjE4JHi09HSNF>Y}v0n0C'
    'b4QjOJ?SOm&sQAb)nQk93HDf7a321+Pt6lJKl!^?@BeWIt;+Xelb-SD*WQ)$ROYdU%7*RnK^Jhaf{iuGLXks%d}Ur{DkON$J^$qt'
    'X!S|6Ed+D$o<2J!4eYRpal#0Zo1zyYo{R~Zdx3KIHD4VXy5)`KYWMI+lX~pILwnY|q?g=U7Py-2b3aD<R5ZBC6%?+A=clDk;m~`h'
    'e8Dwu^!>v4lXykGVQ9X}{srxgaBkbvGPUkos8BH9dM}TVjIiR#xo#+q+G<#k$iZ;D3W%%dkZ;nu(QNypqISB8%=hkNx+4QJ$iYLf'
    '<aq2Y6gTumh4VJyce~5#pZNG1TEgyQIih8k@mcp~fQ0$|!kPtM<g>G}IeL*(yT2P*CZ7Xq6uxr%bigGe2PedkEX8~C{`$xM)vjxG'
    'G^UUo5q|CNtw)Yq(X*?>V&`4KtbcXh=3=8SY`%2dJwDReW*z1i&1+3@9QL3^7PR0tFL6~L%0V4RWl`ledt$?0mbXv4lO;c=T-82F'
    'J>&w*ol$JpVNeqveDF5JgK5FhV;S{Fhfd9HXCgl%_eC!gEs&>n0X71=Fe)!y$zkT9A-XK95PpWu&PPZpS~$6-q2VTX?Y1)qLdl@('
    'Ns)3#a)qqWX=Xu=rsF$Jw9q9-hzD0DGnQtm&MZgH>ABOpl)rNGy{jG>hFveh7u6m50H$BUdYK!HrH$s3ijFAm=D|6B+Re@O<C-yK'
    'S&sdmFqyBfNGXg1Ts*XP=jTQ%5ZOb|f40Hv70L4L8MK6}9R8SV=^xkmRxoz9$Sd9qBrVcJl4}6-@aX=#<q*Oc+n~Lp^5NtAS3iAo'
    '_5S@|D{+^8^ODITLZuVkRWd7q?z?sI1r8^%orqbsWAvQxSr5B-N`_61RFpln$~-G?wYd-^Ez`ClN&1G8Ga#1`g^XAwAs4Zn7j5iG'
    'x|i@%0w{c#DICsn2_bocmg0MNC;#KC+ow;$kcl72kT#;EDlg23PGKxNQDI*rsXmFk@!<qEmuir+Q+~fEg~4h>XYjU4T<^SKL}<1m'
    'cmh4Sd^|p2tWL)*BXWIx^9N7*@M6TBGKQ`4^t;jA9f6+>)%~v7O%-Stw#`TMlyY)x#yrY;-e6%DPDR2&a34ICN6vL1qWa18HAEAK'
    'NLbKg#SRue&!ON@pcN0eLikchYX<?Cb<U;z7|>ERZUT(v*gqjB`}E@B(l66C4Vz@=>qX(^04aFhH!lWkk=um8bgjgB#K$)rI`S^t'
    ')fOod+vxeRB-t#Gmu*p%X-n3zH*ZxY80w-U5(&gy73^fpsU2y~nL}zUk_@sfScWi+Fc=btZxl;fjNYGBWFy$-AT3J{ZzL!2FPPp@'
    'q4=rBB^iS~{QVMUcSt2u$%CA@6eOnvlWg8}j3z-YEdVp)TC@3;{tnB6c=}|a>wcd#jIVWkRv3%lUP49va}Tl(|A|V}?&Egg_O78A'
    'Lf-L0yn)g+z5k)!U!X7KuhY#m@+garK!Yt?;W>;CvE0mKNtX|5be1Pp42H)h;7A?@j_X9TnP?RpCJZ!*i{tY{q;8(3<usi~9PHNg'
    'z;89eSru9-aKP%aLZLP#I}P+gVl{>`t2rq=2ES@`O7mzVs_Z6Kp4dlK2X#4kTn{4|5&O2>Z{B|E1%_FxK1AtwaE+Q}MMt}jyWGQq'
    '*aQsK)&p1VIpWa^kQZ{IcO!^lir$OXj{YPz2LsIriQPvY^vci!pPM3P-4HImtq{47f<1jEWYu~-aHKvFjbEz9#SKv}{{Gr0^RWDS'
    'sC{|h_1?UFGENTCtXx@NPxRcR&ily}M#n{#S+k06Jj8F4F0kJ&@O+Ma|MuNqKL7t^H&o6_!ymONS;`&z+2Q-gK6#q0Y=tCPa4eI~'
    'K`b86L_C{hf=Q#rpwYDvW2O$*#jzxGw06JyB=AYe`RKG-)YHhexkq}l8(byjoBtW@^vroK!mfDXGV($vuoN6x*4dqd&X(Z78qfTY'
    '8ji9*)#9a_zp3m}-t0h-z6l}=H+JV&dJ38o8)9%p1bSLMcqh4Ky(>wy&PgC2N)f_cn`fhyxJnC$9%S7(2=QXlLn*Ktp%2vJyn{rx'
    'lHAO98@j$fL5&<U9kkh8&&WhI9n8jeE_e_Tx^^TexC=G2IVI7;a-@9NcKnDSP)zDXlw<-Je$^xqxoR`_Yv7r{FU*_jCs}27HVeD%'
    '<KCi$fy%#+3hsEtX8}i`^Vv?sTZ0h~F0E6LK}R7mcl+e;n9*Op+Btl(^Kk~yg=4ptWaxi#DiHI|dCbe7&)c`3IP^2mJZ{$<*xDh6'
    'f1#048hcBkzu;2l<a<P8@YX1g&PDzK*7>EQY7QZfX5Eq4`|hO%xznIQrh~SVrRO2eWqW0^PFQH&ros&{Y<C#3Hi`7Z)*jvc`eNrK'
    '5q2c0PBnMbEZC*O7vbfsk(ZNxG-9NsQdcDdg?w#sn8NSE-BS{opoMCCT{@C4Y6Yx!m9*`{z+l4#lEky^HFx3?Ji~CK$CZW>hs#cy'
    'nGTL#1+=*AI1-VIn{Nb)un$VAssgK4#^ic4TEUPn*acKbU@8ID<FDIPaIIAa4{i5KJDTUh(JSyWX)F=0ah2R)wL(o2ika9tWP(I4'
    'rfS6#1cet{p&5lrjWtE?(Y>re4<&!OE42kL%BA_fq^>Zs2BBbe<UYyAuYXeU5ewn;eUkQ|X0QgbrXHv+Xm?}rrPWf&KWGE=W2~Nl'
    'KdR75vs5Nf>=I#AXEbtVix{=;9&Y&e(O068@p0$`&BBE)<um|rYDL)2D~UmGbe{W*n|l(F=t3S06u(PsRN98<7~2oAf^>_lE{>Hx'
    'ah_KejkLq=H&aixI-lUhJbID4j>aA_><+0}HN9Os4U0AvG5&bK$Q97@#0Zm)4<QDH$%7<kD`PhmqrMzK5DMpy4+#DY&#-OTe0<ki'
    'A6NsE4|+Jr)PjhL#NE;uF%&jr7&ZoiWJ<Rnhe`Wzs+=M&T0YMpz!ZaBRZgHt4J+)wmVh_!)9Kl>S#P7{YCdCn*l`@Rvd5gl{kb3T'
    'bnSV3FLyNTZHRWK8?AdeiK&K2u>R-Cqut-YtjPTc)h%VZ6e+bq$N}Ip%_PtF&JmeX3T@<36Jvp#Xzt!FRAWL3grWuzEU`_se2}hd'
    ';$D$CBC7HvIV!Vsgo2SG4~xI*HG)69)7sb9*BQ6d&{^|vAqU86k*yBgdnb!?>nStm4hec-qD&Tp^q^@DWAzI&%l&EF0lEZOyM(F7'
    '-H<U26W*C;Rn-n@x~vj>mRldU)940^hlx`(5z}y2&xPp!4kcNn<<w+k{z_J+h#IhJtBjgE#&LzjAWMA;nmV=0(qLpI#}+x`2VcqR'
    '=A7`IXLcQ@M(XH@FkUAhI3hCPHa#0sNR^Y7Oz6NnUTrLSLKB)O3x1q^RyB#2l1n8(qWym&d7{3kESbH9ahmpFSw?;`$`rTC?iDR*'
    'sh)>&ctRIPPkO1C4@c<Itd$&(kpu?TIGeu0P*fs;I@zjEch!!{;=YY;9?2o8l~5ZI!`9rO3&>;G5iS~Wa%WB`lE-uLA~IK2E}vq>'
    'XP2|f%Z*{BoYc9>&#36kPJxBO806Sem`9cIDY9qWzGV6k#$ySgAod$eBv3&7mP;Nv>O?tZTCa{^Q{w387NxMShSzf7(Psz_Hq0@}'
    'cE&txT=F7~e`p>{ZsWcS%l|+cU&I3vgsbo*8K;)v{ajtG(MwRY;MzmGMGP~l#9;ASuV9^ejHz$NBzZv@jUy7X=3QO!6-aaC)<oij'
    'Xu>q^0x!*R*P~h9f8ne0-RqP}3Z%aqOj5I+bEnT!v?SkfeM+|}S%laDp;xt83SG*EsD^VPnJqvhQ>0m28YA~O`ngx{8eg(N9hocD'
    'T{<+*3s*$Ysb)IU^#L|QIUMz?-rX{)5^hPS@o2RV2*BVC@HRIG?EuAjbGS$eS}s)m?Ji8sg;!Jtoo-pH7ImxgXoyQ9&PV~`Fz-Ub'
    '6*CU9+a}BHpq1!M1@)scP8ypBUfH=KtjC}wW^e*+TVhlO7gm(9@_-0*aKRL>$IXzerk!6>*FlY@Abm&^s6^3(dw7dBD1WRZ>B!W<'
    'T8Y*X5XxU~V+s}=NBpIWp$ZuF-Sz2saDbswK{t4J?*O^U8oDTXaH|~?Btqy~A#gwk#dmV6BP*4z3qz`iBz6<qfiX+U!wTw-a!@?*'
    'LWBr1$B%^n<L^g?CRkiS$712LmKZ<vqL><QB)zUN%3};(-#Hh|sIm~}tWLey8Nn9BE0v5ES@fhAi5Qop0ZOJl)_M7em<S6)65pck'
    'B9es9R1Gpd{wXjh^`d?97-6B-De2(*4NisPBGrg0!9*O*sP+M+7)kIPS)X%N5Gy(oENT1BO$Xq7GQ_*Ot|Y~hbh!Yrt}b*gqIn81'
    'IPFD4n5iQ%7gyFOAB?6lum=-dwn{=5^NJzQ<r4*5r54|+K2WQdx6ES9%B<rL^H1YzDYbWs=O8?b1~|Bb2*P^&1g$tcW(>0U1Bnn3'
    '_P~XBQK~;6Bglv?%^bJS8tTy$1zrh=@~rztlz2QWP&kb{911Sc%E1>V31B#@T#qzVkH#G*?sH0Nz~(?Uc#!gfd6zoIgd^uLJ~F<M'
    'RLh`p6d2ZtOK?=~U*R29g7f5upH|MsWn=eblNYgk=X?&99l;rj=|KYZ$(al)X~y^1R5?J<I3pB^@iK-PL3c3Z5kXSqZjuz^0v~xi'
    'O~mWDL<gFY#kxFhFBDrO+&Tyo2*?HHS3Bkg-z;uDx2!<Imv7#C8wc`kQ5O4?OSTF&15{jLCR5?D5OrMX^kz4yjh7etVh5a22&Ig5'
    'qb#E_R)u1LBN>X#49`mxw(!~r2i#RaJ7}$W<OEmc;%z9T!29M3^<>F*QMg6r(J(kzV$;df8etB$=xG&4mHZLO^v(`VFhoc$cIb-g'
    'O?^CLBBf~Yl=W<n?URcGz37)*(mRZ*lb|w!qaX-eqvbm@FK-33LteN{XQCB#uws2_2zl{&^H^3dp&){9fNsIgHLq-IF#0t^4lFns'
    'dz@WT_VHZXFd<oR<x$z!DW#-zEkQEhr(=^G@aY@oQe$(CIjRa5o|a<0IMd3Ve-<BfnPi$*YmY}N-_U(4H64j&nkf|u#<R+!e2c)r'
    'Zj^*`4EAi)&kE`i&wTaFe-oQDP4Qp`VpXr$wJ8uPdf^cJr-(s0<%SP`^3#N8FGgu7h3Nb)u8fkW{8aQ`Q<BgX)|wJj!gEIfzer|6'
    'D<T-HO5L-|I?x2n7GZ_*moFzCASx5@7>ST4IApCw(3>}f;&6_#IO`)@MJW>9b@N=4Wj;f}Fp!KYm=Gv;^J6TBD{vfVF2}LC`hth#'
    '^ab!c|D;`~^J`-IsrbYY19uaGmG>VJ3~n60SoQLmT<Ir*reXLvQ)bh{yRn<J3pS0FeEF-L!&QL4`f$~$q5fzW<sqOdcbEetKof&X'
    '09FY7L@U(-du_Yw7M-~NVbdMy>-PKiL*Xmni|d6mN$0MDLd`U>8v%NV5pJSx5uv(Xh=$JAc=fd(l#fm_L^QwLlzSG~U)Wk3gK-yS'
    '`J&5;fGC-plgZPXEiqD3P3=e6m0J5xP4uVQ-ON>GiSR|YJ`;70CS60UJzqM+{OnTw;DpR)$I+nB8~72rc*5@v1<IxRspUt3ZpaJw'
    '-N^Un<N={2dzq0ldPTs~7?J?N>I)#Lgl%G58!$~)tcgBBDY9gq<*527FyCG9AZ3)_=@TEfaauzsRVKI^g4mRw1j70%J#h6Gsp=6B'
    'SCDvBAw!#LQPxYDlbnb@hM_A2uf}Tf)I{tO=c)q!Xow}t3WeEQ>e<*I?w#W)h$|t`!rIkjf{fjdcVd4E?hhRl*+vT)!q6bX;-`Q}'
    ';!Kn*#vE~#nIAa?F5<nX#8d%R#02^$&y|(?(}-`PQXU9f^+rH(FY~K2<FbXLibT)2N24ATjH*<jiOLnKOoPfkM8S>jIaZgUrfh6z'
    '@&jzH@I(~LRIR&6X{GpD8Stk&(79V8=GIIjpZHBDS%fR(kkTO(5sO@G)Z%-4@>FzVsgcue6x&KGTCzW6aq~*Qp7`-8L7Z_k)cixn'
    'L(1doXED<eCCKuajA<WrSOcqS#1n@hc_msI#?zsYCX$E~`{RJ&G_<LnvpsfWO+9Vu6e9|bZS@KiC4y$yK4_9fMJJmeaknK}Zs%~W'
    'G&<4^$eM+V?37lQa=DP<YLk4p*#uj)N9juC%FluXBU3=rVi)y{&X0{4M?F~MprFJpcf9~}iP2&tP$B&w2Npb>2?rdRLk1&g4>U=_'
    'Ng++7gN~7S1L?esB_*E@?wNNwchPRb8Yt0_1$h@4Ke&5X42FlrZefaqCdLCFhx%<ccMf&LO14KE)emw`+o|buE@7zZ#-(gn`PNAv'
    'z)hl1Pi@6CS!$y#<}--BywU#6r}*pfodW;w1E9uh^cd#MU@B3Qlk%aURg$$9)aMRQKU5vA_Q{uE0GB$*3-nSFP3_@m$twAd?W+V9'
    'odn6kGGDGUp12ytp2xcMa;;~9%Dc)Wnt;;FK$cNYh(sehpII&kwL7UYE2@+}?HqZd3U}sKIbFq>3%W33Ga2F~8oML642r)YjZV|F'
    'iS#}~;xYaiV2&1JMC26b=9X)b!XGL%Q-VMe+eq^)al00GxHR;&4ZbVDV3jFfc_&ecVW{ro6BHn0hrC<~1}^+SizFcVlrfDpJxHg{'
    '9Z4xuJo2KN*kB!9@Rq8KY!I*RO~UEPluMQ4zvM(B5{%j?DSl-<I8Tt5=q`ce#LD5}t-YWf;`^JguDKyhJG)YpB#4+@?l@|^(^yPF'
    '`~JBJk?4``7VM=23ndY4@Y=j|sCJz^{yOO-<<9cUTdW2OQA=rAftrgEqi`lSrOC4@C=$*eK2~EW_NB+%ge|#)qczQC7JmD~uVYU-'
    'X%#Uz!5H&9n8$Rm#?W(xA!2q6&W%S}x@u7T8T8<yq+A)5uxCJEocN+>FR*xkWWCe?$J1`!-~&cQ*y?5=XW#uarB+Q2d`10B#<CJU'
    'I_H3c0P{ruSccrf?{OP;4o-zh3z1NfJ}Mt=Mfc9}if74KE4A+&V4{dYOHqpMB@-}As1D>+&bIqdbq^J0nn0!eI*($eJmh_b+<gUb'
    'vfj*8eXLh?MKCE6FeAI6kq<|~rLOFzu;sRE<ywyL_3N+uG#ge{L=cf=;fbGs*kXx=j0CM=3Is{rex__f5nIK2VjblL5N4Q*(sWfv'
    'umeU>BOf%2p!q`HDLvk%8TuEZGilGSXibp-wTu*xqbH^iQJNTs0duy55zmOx*WuU^KOv7HNXHinL~_1RH{NOwD4cc=>G^C%@9zrt'
    '+v7BumqVD1*#HYaCDclJX!t$b1B&Ew_(`#rW<FW#jsQ`Ej=by@M&nQElh&3bwv5&kpHiismM0Jw3(&lhwnW{c<~OYB^{EaX&qO?I'
    '!f6WT)zL!>mEm+&fuU5>fJHZM^}sn)I<Q-}P*93118hn$hj3(ct%Su3qkNVu9ANp5@{IvHgquw3(o5AcnnmT_3FrP8LI84TbxlY('
    '-pi@hrz$7eh*=OW?X<FGT~F9lB7!^^H8E~QoUGvFX-Lw2R1`U_Dc)34dnFkjHEtXQOXBEgdy3jkwU2hW!v6|Y%f0r>zEVC?pD8{<'
    '6l&%b(1tSNX^`|vS7(p3&@tG{+^UpJgQZ9$k^`zGTQ{nc8;33|V$vXeV7Q1Tu|bOLg?*%lx-ij|Av0u{)A5B}cZ>FpK&pijWbPz`'
    '6cxS2&X-@7m$&Dkcg|c_St)~#w%G2H$MdbLJnp9Stwt*pa;{OCt1ApZNYzcR(5-;b>rX=5k3dZhSASIwaVHdTiBuImYmty0PSCGJ'
    '4!;>Dt}mJ#`{cxOI<2$@fb&{f&3v*{Ow*cl52=*nv=)17311ENHd%)`Qokp9GbV18Foxtq2LQ8~xamBg{5IxQH2AnnS2&2kJE--c'
    'nyR6+jBKq%mhk;&CZQcq3D%jVh8d%4_fs+6T=nE#0<!Kyc+<1pW^%H9QViSvI)Nrig1)HvOhuK83L3{_q6ln8$V&A2LQ@(=UrFk{'
    '#E3<nENgQoI^?0jr9*jr6-rb*l3>!3D^#`4p1^1YP~~){{KxEqXzu6xJ{>ETT+U+xmHKXyzyK&ULO&%YrD^L{jUWRH3M3R%W2Th!'
    '-yAsojLNyZ_<o2R6<MY!g(tk)8y&*9sc_^l(!~zK5Q9^-tCG3Ar%|4D{y5#inW<9f0G4=JJr}X#i&~r8`C7K@NvUU;%!Uu$z@d!7'
    'dG}U%XP{|Pn(~nu^}M+nPEn$ZdGHdW+wU?UQ=c<+HbxRMB9vC}{sV?aJF>f3@w6$>7VZBOtxS}Z@u^=aVqA+_b(N(j&3MxMxV3X_'
    '-}@BkvdkV^i3t5euSjHFDH2Ie<LJK6ud<m5Q<#@9`t_N;jZ_hQ0Dyj_>1RXMQH7!9Gy$2~3Lk8SG^B&o;KZ&Jh>cU7RFRbt0*2_O'
    '!m?CvF>3-tK9K6BikW%U$YdD#7Ri52zD(+MOSi|ZfyK4Nmvk@lU1BlYEs2<rD&JnB0DhHv)jyN+FKU)bgiCdyRk-Sl!fqyPn3wQ{'
    'T^381HHc&1X%e-7CR@7EKoB)V(KyjRgiNa1Ijz$)XW^C21UXWPu<K8Q0EDooAas-S<!O{#7$pej2}>dxbE&9zW?zb`;!+C}!P3!b'
    ';9Sg`K01hq^a&`3PB4!#RJq-gc|T3w4Z5j6%NmVU`rGAIlW6mNt2UxX>WtUG8y?@6MuA1sEZuum?5SZZHb#_T0-KiM9jE{&Fqi8x'
    'Li{XVh0!jWHf^m?NEuut2*&}l_R?`o^Y7frU8onC!?ij+e^vLgsfz;efOT-Zem$1)=tRdwDpZZ`J{bF}_$Z2ywwKj8a>I#q{k5k~'
    '=@zF#SSSXL-(Y~`Lli_VRrbGt34-48+2fHkol=M-hQ5e26&cS80Xi!I?miw9kG1(t_9m5qHwS!CY<`}A-Q#R#qD97}*i1rt{3i4Y'
    'Z5*#UVC)aFsJa7H4IDc<MuQ4Rk%esjI(CmGi>rb7&BYbk!;UB=Ar7IkDkv6zRNsC326sVD^ji!1`{g8hSO)PZ4NJ$gZUugbAGL!G'
    'B#R+%`ORQBNU8`8gG4R{_Opn~{lJ5pItolES%iifmv&R{r-auIntOU2vb-Ee0WBOGQm#!93k!)F3S4U@oJOUx3)6%{7pE2cPQB2M'
    '_9<68%GA1>l&X}0ff>i0@s+&P=KvEtjSFfgv?&@VhGW6*=744ZIbKAe@^X{tC{{%*NuN0}c#0z(GMYp&Q7slWc)K^?<toy37YvvU'
    '+~TPOth*g~HNs>%PFMm{0!Aye_|DCJsK#$`Keiy>ArUVBHi4(z&zm8*kIgM(yK7w1+yD4(8@MN&f02gp?Q^CS<(KLwbwQw0Iv*NX'
    '3<401+kc9>niT-CGK;TGFi<KXr_LC@ndr8y4X{^wD$bHn7Ij0bV&iR+#o*`<zTnLWC9goe3;QvRQ4!5StEd`fMBK@sgBE|p1%N6L'
    'sNt>`;-(U$*~z_Hz*!J-CL+qJ`ot}%CR&GB7qLO3S`t?*vkClV-5-tWm+nv5KV{D=?ko0l(-tx32qEp3nz>Pz>;Y0r=Y>E8h>}&~'
    'xU#yrin_);kQF8pnG0H~qN!2wtwGbso2VIljeDiKbDm~JGLMl587h@KS(fEBq=cqvHncdgaH1@ivl(;ugjC3bqVt6S97VAl*_4rx'
    'WxTx$7iCv2N{QO>iCHP3Q^=J=Y&#~Tk=9nw9+%Y>AylLXK&%v2LZIZ{j@T1q=2n_Jj@rW7x1tL6<Oo&NrM_x4sJN7cjGQ6Sv+6}K'
    'g(z4HDl#hFnO0z|g7Y`R4n!jlAZ0IHx|Q8guA*n02!lz@D)R+ZbGH1Gr3w3O3&1>4`>6rNXkA(yP~G=nO;ME`3Q9sw$g2|($z%;t'
    '3e~(srEY$i9tI%{d=4@S(NNX;z!5GfID?^SH|myW%5p0>);P##;$pclp3cwDEBXF9I6%)Q;r*9lqpfiXT}+~cu?)b9Lz3cXLR$Pr'
    '-f7c7F<A67E5SB}Dx#~VLG7(pD4xa1b)`9}a1=aGchdeXkqBmQ8&w^(o#>~q(JRrP_EU&6J>?KQo2tWHlg%JfChmSxb~)kX24dS^'
    '8qknpvL&h2GCjyHO1@g4p;;szOMTkYw4d1lOTYQ*%=V%W7|mZ0gGE7pps$l;QBi%NyhfGz5nR;S1Md7Df^&w;;%W@?hcbr>df1DF'
    'IE|e%B+pECGrjpuNtZB0QB!GARLDXhbeWP{)n7#h<iyuwRvu8_zlx=p^iKF=f`J})maf(Ce^qa9s2X$N?<25UT-Y)dsEj(#2ANWy'
    'dPP^wg>MtI2$uzbDqNN{h3eQH<(8@N6#qWQ;+itrF_X)VlRncG2$?~XB+l4Z@OHU-ni$t!laU%NXFff0PdA(SRP?eOG{#38Jsd7W'
    'AiMLxzgwi(bOVXZc!zhwENMR>Ay4D539TWWfg)gAky$tcGi{pn0jUL5r3TAt^wt$(c1uPBPE){O06(s|*)J_4#g(y63%?pv%m95;'
    '=};1#->9g|Ia!es_Jr8*gg0weu?os_R18IMuH#71C^`}y>`>g4pfnZLMfg7+{IpVo5Oxp;gWqa)<Ziqi5sKuU4gy(dRshd^v8nVi'
    'ETMa)2wqd^mcf=<-jrA?WKPLmCXhnhR2YYGJ~6dr|5aT2@V0;{q>)5W!Wg20L6?>hN$s@Z%4Fpo$*Se#6}o4D9UPZy_!y~NRUx8%'
    '<qnI8H>)M?rg!t3GN~h_lD6v7AKncbcVCa?#Ui6-OI-0{_c9h+CRz@7nOdPA#-XUata?FpWV6~`Tz8E4g02Y-k#&&`972md2VGN<'
    'pFr5<-mwl=ZF5Xlx3McKlh!cU;TVeKEsAESvbTd>;-;THrqN8kAIW8Eb+=Dm<Dlb+qksgzia!(um{B3`k!2hji>6&6V`aFd%~zf#'
    'f9*wfJ3eQzd^xxE`mcy160H_YdYI-nb}y_5Yh?|nAb6%!KR~RZ`vAK19;GF3j=kL%m9l^jDf#TAm?{Gx%!pi+=&&<`W@r3%hOFS6'
    'NCwY1y3{dc24|=#nG>yS_P3MWdB<mZc=iM#eNLa7=+Op6C9QWfJXUMSdEXkBf)I_D9VqW=yxkv3%T;RCgS^s!&8Ct$*p~uA(98>1'
    'X%Z9$p-vf*=CAP=+9UrV2sj3^U+YU3aZbHZ6YK%d3LQwELn*4%#q@y~XVm&UsV41m6N($h<ImM&8NGyw<P;pq$|@#pir+YNk-1aS'
    '=uD?lcCz*%L&=1E<xLUPsc7uP(Oj!)g99pDY1pBXq7oY=a#_&F#MNQZLR)5XWD^>dvK}rT+%9z}-c~Ol%|VtAA|c&nmUOd(3Y5_b'
    '2}INBU8i!V^_t0BKGESnORFh%;!;zy>xbx#UFV?P0U*h&Xq!p}D@KMjZ2w;G9N4hX;%ObBleQ~e`1t0|j0ZyGnDqe$iazm7-S0M)'
    'v(cht-3yz*^2q+%|8$q>y5G0yr8#?q(6#^pd)2)mMJi)VshgTzt^$K46NzvPTni9Y2@sV9Xq6s~g%nwaSKoYk`|i!Judh!>AI)uo'
    '`GrOL>EezxH?Fyxn!*xUue|4g&#ufPrpPQ$lz>JqRJOOBT#G9s`d^Dt>e?fj08^)4&5a{@2F^yAZDMGn6m*m!Tzf;bkH&Ej{m_^q'
    '`s&CXn5lX0!PKuOWJ>Y$8;-!;TX&@shgHc<d{%U!E=RFEIy1h)qpeQ!Lz=!O9-C!Xp~wr$cVNnCu$o|J6!#RnQdDTk!Bi-5Y=}y&'
    'AW##?(17xY1r0Y4;($^ln2?wNJXoVOGQ*q>mp3G0X|yFgQ1s3{#%OGegSel2I;Mwdvwu7Tg_Rl|rO(oG&dxl3T%Jh9AO@Jt{RIwY'
    '5n916u`xQ&yNwP{lgG1;Pwa!)i>7;IFcid6l2~a^ufF|uKPglqoRmJDi^EUSrmgrrKWtQfxk3B)@iZ;Jm2Wn9QPjUcadyBdkizKG'
    '_7@TNp`dJB|JcanvtW`34_Ce8*@NOwgluw_B1NK{??n^eT+|jxLb>XoXKRkCcw9D?5Hut<B$Ce)L2T7M5*|Utd%!ta<O)<~neGyF'
    '5t%3GEwLD+?i^D({xz`$4^nHW8exeXZB$AfBCRflsT8&Zpatud;t-4os>-AVn<^Zg<crgSYKej?i<w+_DH-4%p(|5zGo{;x57-WV'
    'D+Bm^CbUrje7s9SN-VBH1q@jV=7@p9(GIIDqYy2~c>`1@i>BrJ%gBArJ4OhcUMS-x!`ml&(f28P9{TB_HU481;xI_8IKp>haOQB7'
    'Ca%WV_R8Kbea5Sd1s+T~!IXQ1O+1(WSC4;H=2PAgq^l&4%hOG?J}q5zAl-FxJB4FkrH8xlYH8}Cc#=$oW8sgv1;TG)yDClo6K)pt'
    'a`ndd=Y9JLYir`E>kB0_YJpx8$8yOvA@iMsAx-~?CXuzxJj61wM1{mIH|e{~S*igX7eiLGeqAUHI{%)3Cun+d2~y0nc-}XT^)LSe'
    '-fMir'
)
)).decode("utf-8"))

_V56_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
(
    'c%1E>L600qa)tkjFlQY&!yzU4HX>&wVkwP44p&$Ugdo6c7%<j{wQq+1yG8bNRb|!}@m^%sj9|bgHoJSeG9x1+BVN3S{N=wd{`I$i'
    '{QYnLxcH|pe!2MR=KcGNk6(Uq@o&HV$G`mNr?)=+=kLG$<KO@GU!VT>%f+`J{`%`r@9tiIcy)jA`$s>2e|z)k#nrRlzxd0=``fo~'
    'w{Ks*`26;#KYD+A`?~q)<H!H`@{8u_Ki<8&|2}{G_ix_aUVQ#d_tmFo-~9OIhnvp>dv*8or_sVE@4vsj{ps^(yK%k0`_PZ;cTv50'
    '_2&;ioqzN55B_}n{{Hl8nMw1q`;&HVyQi+-J`JsV{^obpbHDxY=I!fWe_z}C51*uBKlij$-E+Giv*!Kw=GCn`ZBT;#7ao4|$NOfG'
    'fk<B67;`><JreNE{q4Kt8M~#TU31<5Kis~(`;irGC);2==WV(X!|7M!_xeS3MhIJUSqRigeDX5ZjTE;pKTA=p&!0Yxtb5qzH#W~8'
    'RZR8Yp883Vx-qOOkS@vQdz}CWHH8$`mOg#)B;j$b=zg%UP@9iwuiB@_@;lpSFQyw;Xk$Az;{k>A2LbCsN<yo#8;!FX&#S8;w1k$W'
    '|C1vZ2$e%D(CJSGN3nNt9(jde_tF^hb+PubI@oFEDE{Tu{tSF%spmTIFdSzLRjF^D;z}J)(j%n4d+fj?^55-WsRv{(VZR!&JMQ^<'
    'nKvoMiKpUz?7^GEp2%jL=a0=_BcEdZiSwuKkKMg}d;9AC*FW99yMOcc%|Gvr?fQfKU02~SAc}r+@p$?Vg57+MAva(DWKzx%8w8(l'
    '2HxK6HDTim?7Vm~De$DsBaX$cBoGe+W#O8(Wsg(H7F%<3+UXPbqMkBgo1c5+fumtKVhXEOJE`VlO<-ey4mdkPGcmhq@~7UUYC3%W'
    '9kGs&bvBb${QuBAkEZCoeEG$7>cAuikOMk;;Dvz9#Mzj5xj9TR;aq9=LOjNDV%R0@;UXtCvDN`2-~JIwFd%V>dRZgZBJX$Uh{(}v'
    'K4kp4#1TpzcAF2u87l(k;g9>zJb~qxzrT6+ml<R#UyD_H#v@&ORhFsD;|i4p+hTz(xL^eq$7~jg68fVm^C(j#!87gp<2k766J%?+'
    '<zPE~CQKUGVHM-#5TZ0ik3;-2CSM*D%3ar7Iy7|4^UAl~)1yl2XLsJ%^X4JF=GHR4)y$szGTKi?gR9)WBV3QepHcApj(MW*1IDk!'
    'Bl5*TQ&sjQXl;Ze+n$W6C0|2;f~nSPxrbVW#hx^=p<6&pQ1XEwHloA3NzFzx>yLoisU@=4o0qBd2lS1Df<WYWoE@lI=wk|}Y{H**'
    '#p<8r_!tsl_p%(RvMcz!dosYf{Cr`#0`KtoVp#Ux;neDHMwaR4fQ-UNuCI33V&u4lIFPmRUcbBhsekma%Orf$%@g*VwBn=mIufr7'
    ')Aae1Ef>mlZQX~C`?!1l*{s+5qIs;Td&6$9NLv<s-$Q)Rr}8|<VN~36tMM4eu4pB)%;c26*=LZ4{Md>~7zch81ryMYaS#$+kx@r;'
    '=r~+gCUPKhC-ZS!esaMcfhxehiAow*5{!9#hrY;BkUZmD%W;va7EbQa_-@s^cG;Prpmfl6k!W*AdWDqD>9l_if8#Svc+X`nh##&@'
    'W-KpMommcb)9+5NQvS%*sjhlo7*D+jALM%K5?4Qjk}?`L>^GgceT%*&F51rDz3Qf5yJpQ8vh2h5Pnb~GSB3blXvKg<bC167jlhPJ'
    'kHwHlct?5fG1JjMk8xqpO+Vc2T`eF9X#x`+Kr1}5{YD%@8DopL^+ev^zq|SQ+uL{V{#ps5^pg*nEMiMK^<1Tr5;VS%i?47viS@|K'
    'auSwZw+kC7C%FljWL(r}McEar%(L=To1H+~GHol|3X`qo4Cp0<86#Fn=tZpOMH_q8?n4+O0f;@!(+y{N2pxEWC}NaJ2L>Q_?A%vF'
    'Wf$ki3zsD+%<x6O(UxEjIyE8t5wFL*S5z{vf!9YQKp;A>(V;%F)tl{>c!1%X-a66tC*KE!LLck-Zvu?FyHEeVG~<~i)p7o_a5&p~'
    '*1*--fiPl_X+XIW0Dd=E4}xg3cHiCIy}xa~x%n9d-H<dkixkaJJ9(6yTer|@%oD{yBlFrlezQcK7eua6PTU%)Y;t|-Q!4n?-Pu{h'
    'F%ysiIb;S)t{&;U-C#N)2$@nID^+AAt_+U*JjRWFWIW*ZO%V2W;RYNEw2USRtC4xI-NJ&qUXCgfq`~76wyR$<oigfQV2uLzw91<~'
    'EepIt#b82$=b;TSD?x8_Y1~0T73~~qPLYS>%CU}xP3fsxa~rbyad~7Gh45g9Yo!paP^Lv^y2AzCZ{fVgRVit>sDf3O@A9p8twZEJ'
    'di>4lG;F;oS7UjU5tuYX-OCk1@#gTbFYfOnPDX$IRr-B!{b!an+U8lvu2xlKCM=i5=lswsD^!o;;xE7WYUeQoQL;8gc}un#0zJ^)'
    'C}<TvqerMI9k-lp&n2i-8WxZe5nFR~tDJ>O1nt4OkuSgLKmjh6@n<4nR){yPsgV_#2y@BX&hUvmjNKk*BczMMz}hWC)%ms1tDK@*'
    'wUW-l>;NR08U{xQY@PU?4!Q|rGY)PE7ch@Axw~<vnRWiP91CI-niIc_DwU$;TB{SEM}XCRRPT}bo&&LyD?+hV&nE~M@g^NjLSJTb'
    '6Q?0c7tQRA|FYsU)nXz};}LFlcrEu`tCt1$na7jV^zURhrJ&vz(*oWk7dTNV&!rDF06`T&8KLv|Y6fD!cWv@-xc~|+11`%E{euJy'
    'if>A<q6$@D^I|_3g_AOAa8_BXv7ppdDfRHj;RM!SjXPh#xg8M>WmfkfHdu=qh(i}YU$<Tc>x+T<jqmtnGYu3vNpxUPtFOlc*(BS~'
    'j=>La-v0UGoO^X>WNESE!>?UpR`fizm&=FLDIWe%`S6tUrc^d2BcLUG61;7Gg1bB089Yg`)uD&ZSWp&tGtHeXpaa6oxv*0~TT;}%'
    'bceQpYzMFv6%Ei6abxxTz4g6<{r4qIm=J~YB8|T9HZPMc^Q1sza-b*)6S1&}dP;Sy)~Cd@rFo$}(yijv&~p$oI*nA6-aC`y2BJ{3'
    '=EOgW_ID8Ix)~txB^?p&P~&kK=2h{6Djf>YC-kQj5T}n~sq7WkH7Swmgl)9m7}--)tre+8L>*qgaaz5ClxOY*@M+SWC>@$|kx#1V'
    '&|-UgpGR^nw)zxZ1W{0Edac5X3I{#P^kyggvEy;>{fNBQ>PT#AJHKQal&dqcUHBiLnWk4>YSChde;LkFFE2ExBg4Gs*ADSe?Y2!C'
    '$uM&Bet+|WB7sU3AUfHEije8@2!Oh2P|%n`N4OI?V)j=Lk$>)LQ&_0ub3%&;d{}pA$jXi)gVn|CxA~)pSG0C>dMuQ<oVmWw^{f&Q'
    'LSF)L9a~<>kL?(FUz<cF@@P1EkvQjwz6!nq77A%bOGbt~LTAq((s?y5_WWiDQ=27LI}<@D26WO<h`mr6oQ336)BQY(*KfWXo6TWr'
    '-B+0y9b9-SwFW3If-547&EdiQe<(<@yb6?HbU+Cwr&47w)e1JxtV^=CW7tTbl@h(c${ldkpkmt_xPO)O9~7ll=qY*M<J`;1?!`+}'
    '<^{rlKpefULwYl1Tcq_~awpMJJHI|OAr=Vz|Gb}4l%k40jByOAkd_z(SQty>N7bp*t0Eyje<il2^ltQZ<$mSv^YKYaUs=B7?xy+~'
    '1t<48Nnm~2lTR7Vp1br_W^ZL+IiQ&kL(hw5Iptnsv#1e+DF2dYVpOc-_AL;rp?e}2`L+1_(W!)OpK3IvyjVX>5R#+DFDZ#{I7^m?'
    'WDj1p4@FLffPHCI9$~;y%^>zFS2wDjub6(>t&Q%ax{#onUx;=#_Mhl_DaKgq_8DPCFil9wGWaw3YkUPwz~T`6_~n-GlZ^1}dQm*P'
    'qR@<Hh4w?s$UoGKAYa}(b$<4x+s^_aU&12WS*iLG<dcg0LmpOH`v+znoQytilpB;NKR_lih;>Pdqvc_8)Sbj#Y_xks%7z@;S)*8k'
    'jUTM>vqb?6ctSR)>gT0ZKdlNulCc4I;6m8D{beW;w-sShySqC})0%OHvq<gnK_w>NGkd-JRVFmICqF;$ClORK6?VFuXvdg--kfxK'
    'Z<A*1mpyGb$7W;k1d$Knds+|*q1w&=o61(to4kPwv=N0{aMDdah=L4@7_^a!<S~@-$U6Zc1xB}o#Cr=Mh|1+XcL5fyG?o!{MTXrg'
    'VX|ZeKfTKF&d!BBq6x^>1{;mcyGhc=)Hon7*Q{3RxdY8#Raqd#p6+l=M$6h}Pg<jW``vdJ=M4TNfXb;j*l}C?laglo3DvP)rx~I{'
    '*6O!|>~baxWiU+(?}?j+M%tv#u?J?FJ2$2pogA+p>+|6KtJZR6RlzA&PVBwG8xBReP8NG)hGP__t@rM$%sXy|Y0kyA5{aJA(&jf!'
    '*XekmYYUpVS*l?HpWBu^9=1ubR=^;SMpNTv#G;O>)XK4@vEp`Ly9lRS?NPc*u^g$on#AS9=#GJ+pb=BSmO6*{!If>8&@xJ~G;J-U'
    'yZBc-jIV9~apHd?U{b623zE5UWE4uuqDcvehf_Hi5H_8dWJS>KNEu!&heQ*%$c#Gh%AF?a!;Q12x<jkYT_u~fv;*_J^=x5cY2!rc'
    'I-8Yc8=S}kXj_>c)PYDVE2V;_3@q4Ej9n7?)01i}C}D+{U~+H45v!^q4w{W=wbFOG-wqcZ!V2R7LuQg;G5hLxXJ1Y5N?qo&qj!og'
    'JyW$#0h_vdB%8#eD38#SoN}3ah_>aK;H<hPBD0zX@3m}mMroOsry%qX<Yh*THG|1!kQMpcsz|?{+ZFfes4E@HHx{E=AYVG-rK#3i'
    'Wf4)PM1wt;{wsZ1oOyBna#QhEjJ66zbE?^+IL^XKIt1uZ;qnSk`ZTXTaQ6lVcCy-;_<ZP#kMEL-QW`Elp7Oni6fW@Muef40)Kl1^'
    '=n_Gtlyv+X{D7Vyh;_yyRcx|A?6V%A*l`PM9rJ})dM;s&!AC*kG3j0@Vcy46qcgz>Pfh^Q6cKbJ-9m+hA#o$KnhYBb)t96vv5LwH'
    'vU(ERJgK&F$X+4Vh)aKtoQ=*eM7CM<CJU-Lr<NnHSV`d{(SD~8X?o6%b<cP-YUJpPtX*<e3ouH<g_t1Ku!1E$bj&4jB??jveNNg@'
    'iJ=miXICZJz9KRfHxBDbNduPMFRQF^jOzLyDQO$rpDy}Arst!^`PjpZ=pflX?6*L|@_1g^zt`Ew1@TFgiE>6Q8TfVZ{{CXlBbzhX'
    '+!=a5o@j=52n|PPTUC4L8n~F$F)|)x-P#Rs3oWR`;PP(MNQFmHRk}C3xkmGTOx(fF0ktZE4zJk75~_JbqY4Gia9~1y%1T-yRrY8`'
    'hqkUk!c+ws(O!|YK_w#*Nye2d^;m;9?<gFjgNr*Y5Lg+c2n_Le<knLevDl>_9J5bOL6beGz=g!NJ!TId2qo)B(gXWW#wmsN2E7p+'
    '*j*wcTFT({$BG(G?LrYLEwkMKAi83pn25_WvwRQP1TrgHnoXfDdXdWs*o`;__DGT&i0vf@Le*AqVvh{IMC{U&Pj#21uUK4s$4%`@'
    'C;twxBS-;dSV#HL{cdWjgf5S7^t`^Zb_AOLtewN|Iz%hNzG^LGB$d|LZ`(eswrBgUuD4MQyMqj0p!`B!XwWu)Q||NM>I;)&cSX$F'
    'E#UpCJJ$%VM>MfzY?fKv)QIrm>i5Odoo5UY8$Nf=Qw>`Vb))U;OQ$Wk0{$a2$W4mFg3(B#55$SQ0nXG_x0{yKW}k(HCsGnfrM2eZ'
    'tV<2OM3Ew5WDz{)VS|-haVWRS_qEgIGrC48i;r_R%Oy6}>XG_cKF+??h0t=lmuiELar~XmYx}cj{d-U>Azo!ZYHncOJ^&H;Vd#uk'
    '4S7(7qL8pI$KdzVc9I^&B29ZQp%@1+`4T!N*azW;dJMjh<AjRlwdhBvRM=qNQ-Y_7HVDnduaAr{r8<~)Ksfe~UHT<*S*n(RC1BF-'
    'bE|FuXsZ%h?LAGSxlxXYo{*bqgeU4?nWdLZ<SD=uwHk#1gUQ~phA*1hd5*>ZpnI)z>T*ni?v<nGwnUP60CIE}Y3>L!-ds6}2KMbd'
    'px?8f%-@MBl7+e%r_z~Glhkq8nxEn^V5A}1dv7_NKi5meV;R1H0B_-y?HDMM6nyqV3yzVd1hUnf&KV;bZ8(7@p$UYaH!(JXk7~y&'
    'NxR{rxSyKov<f`A*qB=s<;QL421jpP8j`x++nv$4tk&IjQ*ID#YUK=~-(4!PnF-9eRbwMIs#rOs9<9QmjW&5)prY`1MQMm5rI3Z5'
    'ZYnW@QsWKsMMTRjQB1*$EC9NVT<Ysnf&?&zRyCTE3Np^F&w*6q04ZS{Gj)b&Y3%-Lp$<`A#mmb=+PKs#ZMhPz+m&`7K}(u8b4F~D'
    'S~eq%B-Mxu9qT&LN$#aW1SJ;yRBV-QVn{?5D>g?@lf=t0Y-q4o!r&xaQf911h>{yQ!5m4IG=;W1P~3}s`r01#vPn+t?hMR3np@Z}'
    '4mT3ZQYZgeh)=_5(QRSpD=OSy*uU>wix3x^FsyRA4WWad+Be%wx9-C`)`(b<NRjqQ1}c){Cirs^B2R?nP*$E%9xm6-Du#pxyoO*k'
    '3QS<5vA>xn2@OPoQ`Ojrir}C+y;uibaa97-F8U^+<4pbesq;w_)aet<W4T-S1-eBVc~h|zEV7t_YIL!RKccfDSE0BAM9-I;CKU&-'
    '1e>USp*cLzjw`6%Dwf90l{JYJH7<{48@aXKLc4IpMpjOjLdufFp-wR7(U$WS6?w?ychFBy1#LbVMJr9ouAz#0@x46Of;73<+RFD@'
    'W1z)8HbKjEvKkoWBv<eeQ5kw=<(<i_ej1@*I*k;6*f$P)d1UW~Fnd4Bd5ia|vyIHG6#L~i(4_9wcDs`}K8xxNAfOxG4?7%MI?g+w'
    '$J$0EtRQ5&q;nwmRj`K)l-MqJ9-l6=WyGn(Bmi8olFK>=&(RjsO<fS!X}-LG(&Bh<J?ErDY;Kw<wy)Ev5`4JxO2t%Ab%xMy*EcA<'
    '97vb$;pu3*Jz6)J_0?4WSONV|r5UiMydtx>{;2uMmb8WdTH@bO|C&Tr;<REv&bTke@5-{ruFA?M8(5P$U?N4JCfS`T1H%=mxxnWZ'
    '-zBb*eT(C4V^Kc5{3c}sZP0|=6()?w@hFF*lu4dJ>*#7Nv*bTc3X1kJzBlh;DgmS*>i>mLA{xbd>ElW$rHZY{{sf4Yh4+^DaQ>F2'
    'VIr=wk4r(V20Oz#E?H>BPQ!68m=COLaW|LaFJA{E(<`j0%9@CVvpZ8Yuv22=Q!UD}s{+xKj|rGlHE8;!CRCXUvs_oviq6L$WRH=+'
    'mZ{A;b+uXS*@P!~9J>)^+`dG{9I*6ZRF^K?Bb297MDT%}n!+?xcrbX2(SW`2V6(vaOrry~1#)K55jBoFF*6yW5gfbAcEEgfwG$35'
    '!RN?T7C;r?ikx#Q+eI-)>e=L7ar$K1APLZwxKiWa|B_f1#GZmChzji6ylJr5mOtBMd#uaa1!pQ+(g&>RbgS1BVNJ9>5h)?ahMQqm'
    '>cXlQW#<{Sti4f6<m%r(JLG3OH%afx>y#AXAnyf*JG3BGPnL@$+N<f$_W%CwhnxGmRgkl4r#!oy!5)E5W`Hqpj;r!Qj0QxG0YmbX'
    'C?^K43$g-!xQ+_=H=GJ}3ZWmgiQg2HJb+N5f?&I6ZukpRQC@Bi@Yo}ri<d;R%zB$Muw#_(REnPkAHi_#579l<(^eA`4AsICdQ{m$'
    'wbY?~R1(Zs4y#>n-TXY)#Hn%>#h4KoZY{K|l!qRotD-<hWx^14bL@T8XYeQm&Fj)6>KT{r2TgWFK5p1%s&=+4P<aVdDOD7#6+dxC'
    '8OIw+i%lxB<7-@3aM1Fw92>WsVvnxf>h@C2iF#o{4HJNo$otf49hET-vi~#1g9Y!Oz{jwP{aF2u!My;!uOw=WEzOx11*tz4?T#rM'
    '4)V=GNkCRl_#Wah`Mp(B#Blervp@;4%!vwD_7G-^mbNKRF<%>U6o*#Ch_w2b36I0No^1LUYJyvtHWsG2R4%{CVgrMsIMD-&WIby2'
    'DCe&@pM8KSj^`(ZSe<L)Tn1W%?8&TWULn=&>{ER)9@gzg50Gl&*X#=u6FKQpWAdiW9&CQg&Y+)lLRb#bVP=h1Ssp0{FB(-F)SpPD'
    '$XzT|WS`xF;KQ#*dcalkR3#}0ZlYf#vcFDYs%M;Fe#({~6pAty<8WpwowY^JqP!?|_qOh-C+2cc!dkSaar&ucv&V1DwLTUEMg#mn'
    'H>AuJl1o`;CRYrEQ-V{jvwT=*s1-MetC8WT-Q^KwUgAz?B?miCHW-b=+FNDZuIQD!UE|usye!VKI<b+`D_SOW%kW;%O{0+$UyOBS'
    '(87dubV2P@(C@31Y>Rlv5GGkC8?sCUcN;rTq{gC3zcIF2HQSbhfVD8qwhkMO99f5ci;G7jXOFn{ffJB(vTqF%z%y6<qm8plT+$pL'
    '1-aAOjcb5HfR4D#x)46eMGyyV2vp*T-)UhT)h=(UiSt}pZypbc%5vJw+_+2Eochb8L8+KxUx8J7GGFgBbnu$BRiGV1Uj6G(zD4p1'
    '0c&v!l)oCNRf<zNT-d9xUMfM>5?X5J6|HcS%6lTL5Gf>@kC_53*WHIL%){r)cuPJ}>qPW+y6FMo$F;fg<RuVM2f+eClk+cOXF^18'
    'GGHxQHIuQaxvN*6s3;j5)MQy*i#T9K@ra^mhnpP9>MTv@2}Tn(O2Gowl9Oe`vY43LCv069jcp^Xz@PSSYv{%;(Yd&)bmSn4yZiS^'
    'Ifc!XSc1k^vLZ)u(8R6dO~#re5U6S!i>7PAveo-uG;KF_{??783Lupql~N7lw%db|j+bX)a{*SRxp(MNikT41sO#&5=>n`KfN(Mb'
    's~Y(XZdlQ2j7W6~r*w0UPiS=u$0N$BL$}GbFQDM~b?DAC2U=Q@qDnpy0uQn+aXEXzOBC%~+CZwqwn?(VP_Df9)KWOyRjYAaiaz9!'
    'tV|IGQA)iNg(%}GX3PSf{8;yWb2)SWBB<2R6`$@Mzaf;HWVuH)6mMepNwXSwij^-he+e&V#xgoQNVaZN^P6=(P5XR@A}Vak>v{_b'
    '1wskH+3uh!bCV-_s;L8(UyfDWLDB;Rx7(`yTFrFH$Q)OfUKu$e39TYJEXol;DN<E9=rF2ke0vu=iHUJjISrr^8Lp!V9uKa1y+Y;X'
    'rx_veMfZM6Jj{P665RtNa7n$NFI(7j*=Fr`6QH#zZ?6zp3s+N#%n@(H8U(X{8A-EUxC|71nazLgABGKGi&;Na)C~tMJ9I%#D9RLw'
    '&8`=jd;zqjIvrnI<=x}NRGebfi56-;u9R#GF$Il_RU4B9D<STc+@Bs|;5i%?6<Z0PM6uOGZoW4U6W1c(UDPx>r^}^g{|M&SJcY}+'
    'AzIy{VP<Z{R4RNpE9ztV>mbA@ha@`I4Uvkdq}d7rkPj3ZJmCV1AZ=nV4Kf_L@_Lw+T-B?JGbC(8l(nL&9CVh}w)J7kKoWILsKF<N'
    '8H6@@cA>kJQ<maS#e!0t;1`HUZOp-i{qzUUSEmdwyb^EVR8o+~fi{Bnk~dlx%F(6ZyXijKSsN{6h4n3<Hn{16era%ulE%b!$_dyn'
    'AlckHG&5UfUMY4i-Yer@9*p#NnGZ&5vQF&q>yU>o#LNe&gF^whK84d8I2@WXoS#uLYoMSF%SR0ExUtNp0b2$+M2z7Ig+kxd3xmBa'
    'd;))-h{vgFeazzSoVuCi!uaoE@*vi7w*YRT&ihg$ZP%IjWa~TK;WBnxD&@?$eeE<dOgIyXSuU;)SN5N&Z3M|g|4@c|=bZV5=w@76'
    'O#Hplq(!ghv6AX>08BSOD+aA-Y&E~pWK*Snc%_Mwpoy`>s}0j?hk2=;RiIqO8!EGo|6+2w?ke`7nk!ErJD-R=Tt&Cj*TYjy{%Tyn'
    '8c?A`C|YK8h*ij`@T$v!u~!x7J;LS`KmqMXak~m>iAwU#(flMM)!2%qF0zv8R9ln-3*TjUJDyoEP&!c`5SoEnOG7j?Ior=4V`CM8'
    'xnxCd(L@zRNwDffU&d_M%yWuO9of|a7menI1W*y8a32!)c0qK69IO{zXdTt-GMD-51$W29pv_dvA=&KtBGed1`SR=ngf)6JZiQ3f'
    'kg75>^Og&6Wzh%3DwbD^5)I-O9hWkPra>*(f$hS%r4W>ZC@N>vp}4pddEs{DdcaEIhe*GQyPs>@3pSC`KdUgQ+TCQLS7dpA?X=K3'
    '<~q`1i-&#HeD(mK9d%K(*ZX<s_8k63^p^}lw(A$ka(Vh_;dW6T0?!gfOe)!XDAt#D!W2w)WchLXN6Ez#KTvG=xW|`=$(ASsIu?ov'
    'VNq1BfCQ6Px!(ixS5)V@d-R{Nx<$S$lwp)=ma!2}VZj3UwAkH~9EP#UmwMV2Av_TnX;QH;0)>1qOh(slXx~RKpq7o{H0(|S;VA^`'
    'w2qbo0ot6)H*36N^ycUC_jFk1E@fr?YM2ymz~Qb@I5X`(szuCdo-);xhUA#SX2FvTjzraw%^@fHD}y#-BTOPK=BY`mBLyPvbJh+Q'
    'BUgXPb-M0m*`kvf??rvAn|&Q|mPfuz%K0Je0+rI>^vlJaKeBTqpm0$aUfUrF^)?KCSbsNF{#n1<H=Ge_td-CrFH#=GMZ!P66fI@O'
    'yBTR8I56W@uLo)MH!ig_7_wE7>ns-d-hx&qFiny}p3WI4>|HF}@*>*Z1tpuU8^OX?Q-BqiQ?^D?ZJF{5xQBL>60_MFWwd(R8~GR}'
    'd36-TNUw$vd<~EEMbVMris^d^=9SSJn}m|zX!4upqX!mCd-=`c8?DsvA*v%XMRk3;OUNts1ik8QO#ZbFKj~K?y&T85U7arzxAYdp'
    'isCcaMRXTWD+&Z@#EtiWg^qlfb|dIJ3{>S5Dq_eYP#wH2kXF=A?>wN9GeX>V8PBkEO^UAjNZVLPc5MJvhMN&$)z`Iq6FoASHfB@{'
    'Orbx8wr-+XukOYen-`xRR!4;l2Q5Z(+PTohiWIuWn_rMCXMqNd9y7bCdr1j+d?i&meq5o_I|m#@%L6*Oyz5hnd3%SNdn7AT$6uxU'
    'Q#!HL+Es=>n9n@i2j$8kE+oci+FHN;A*jlf#w>M-V3Ma}DGMB&xLHrJ{J&EgtCM{Sl?k;-+ax;^)(W^}uzw%LySu<*FIMc~OYx%f'
    '>B~-m-lhQvn5jUN7q%)(GZ|=;)mLVGohU<6dS<vQ;TdIV{H|%3$4oM>mB|(-t!Kvlqif-%k{gvP1)lR!NgdP$+pY6dyMs)UZgTr1'
    '%4RF{AJttuK7T?ej^0#9m{ID`V<2g>fR;ozFPYpCjEVz#t2<iYh*mdOF?EIfOn{?P^!$=@{E@ln+Ct>7+UX5jMD4Z)-FVAs5Y!HS'
    '^ML6Ol8Fy}dB8koZjI`y<=qR`vm*N^rV?MJmeRP0p27S`ZV#Y*OR6q_?5dk-Q62<4YE&K%8x%?2cQz6d%s2(mFRP-UYSDmzDGE_!'
    'Rxp-ptUVSK?#0=72|F+cR9%|WevdrgVG4oKsxdfLRyJ^nd&w)QA?^%3h!k89lCqGin5ir^5IqVmOJWjrrlvM3D%&WL;N_0hOD@*A'
    'TIfKpHsp3)k%x5Xlx=YOt4dtFc(b9h`T&su?#OQ}Vksu($oT1ml)F2Lj50n);Mi?_*ixCQ*>$1}4-VKWS(zbkv&b=_5LB!u9#agU'
    'OaaR`x@bnCBG)*mH~K=)ts<q8HXl<nJk2rBFtfuzT(x55o9qGWYPPJ5=jg8npl)#@$<AXsBh0F)IhiT}JzD9ic-I0s;tr(S?~)qV'
    'yMgO^iL$;H(q_WO;Jn#Jr)6i6S@rSNGTP!$pA{NoGq`KZdsN=c>HZ=j6!H`qMi*1?vtP(?9<!5FOOuuT<@;>|C$uodaoI0T4cpas'
    'c($lYFLTzI8X1M+pymo099%oj6l6OB^9s{eMEduR;{P>#SkCB$=?YrL{^~?>?cn2<fK0^MN8oy=cz0x_QcO6a8Taoy%zxO0)PZBY'
    'x?mJ3u5x54=n`E9R0oGhVuzx`>h85NR~S0X5>>~*!^OdzV#8H(uv*;;1qC~L9gxp9k0mfn*#1%QovW=C!#e#6pN>OZv37W!jKT;~'
    'npuuSs4D$~0DSyyI<Ue5`U;0tQUfNT1m0lkd@l9t9H+t=Y8<vXa=~8ocNlH2H|IyxK!V`o+8cyu*xgouvls*rLV;hzCmtQ6MFk4t'
    's*XwtaslvrECu8<4hlwe$b~JW4O;6Qo{r7H)GC$=MFLhI1*!fCJ`gwuvywJL^Cg4b*sRxtTDq8>pU@F^?P;uF+`d|tQbFjfU9v5N'
    'f`#<FWo68$ogrt_z~*$8TDar9Ic0YQv3}@W`tV%srT_)8#)U?LI^=Ff?Ul;-UxAOoVaZbuz4U&90fg>#pA!opG4cW!$ti-PmQQv?'
    'G4Qp_*eei?-!zvlPAVrTA{Wl*r-$1sMEnez>)>}zMIQHeKiu5kT`V>2qG!?e>j!nbh}T(%VwHZpjkCC){LqX`MBK+|jIqA5PCZ2R'
    'IMB8Lz*qrGcUXz*3m!PQEh625&s`IY6F-?ryDn#!A5^`EdoPE+F+xPSou>NAKFC$tuIhU+!U+}kE`c;6#zOx0X2X%@!?ab&^Pz+c'
    'w-0t4euVC!{bx>7Ou~lsRd(1<bzkLD{r!6(@&xc<<PHeDeeTX!0*fmBkpoAwiWf$l%13T;V1y7M-vP)0be*2%q=vkIxBB~G2o5h>'
    '0~Pj7K+zB6j}TK4rFk6Uu%*mvK1ID37q2O(O`6hY%jtATV+Q~B4obmLw2l6d5xE>`m5@qJCv4Q49=>WMBAhOO`$Dvj<eTkp*qJS@'
    'n7B!JZJJm#a>wmzFi_C7HdxMRk%;N55C>z|7I9Q;J{$A&F!c4yP@PFtx91f5Q8mpeM#v%h7I+$kje11wype7~J0tn40eXc5+WPj('
    'Ny~+{DbaH7Pa)a*V_iov_~vhdG(Mhb6jKEz4UZXfgIQh;+#j!#5=fdZct9Z?rvJvk=+|P$BYHnq^p0~j9TXN{7_<4x_T+Bh?e?P+'
    'Y*PbM&~6G6e0=C}F21nNJ&SC>UQncqVL{$PT}2W;G(6rbp_G~Cm+@Lj_<pCWUxzvzO_OlluCu`c5=yl9^q?ZG_DP#0+XPWmc$}{L'
    '-50T$-1ly3f!$3ecl&k&4zM|CV~Ugcd5OzA(Un06b>DKG1QxUvqwShv>M#4B$iwN?V+H*VTsOB#0HSx$y{1q>D$)XHA$;Ru@*-Iu'
    'M8e;Gc=Pu4udnXTr#4NPr<6mK!v1RHJYSazzf0qf0VPCodTj6t93|!OpdX&cvqm}O?ondo8uOOL)3|YnvM)X!(6Um!x8eoWlC%N$'
    'EyK!3mLk8+$zznm_TsR!6y?saT4OH?V^Y=rM^*fZ@&L8DJ9z)=32n>BwXOavPu*0&?Iw`k))^f;SxFtyU8;Rt@?%yU!UyS{ASKlZ'
    'M95njY-{eRoMauTa@{D&RJ$?JFoVaOm4=ErwaB!OO0-<B&LrnA#`MyrFYRT2bu`o8aw2pjl!LTPRQIUb{v5m@I-9FQ7{drrN~ASF'
    'Uhroz(_|sC0$0!Rx>k{v+~Tum<p~%jH=UT74}&nRVB6TBEduDsJ<p!)L<KUCoMw049r?)9QF#p+E%cc__Ao)*VmLv~zsaX~dhm6<'
    '^sMI<v<iE@ThY9yX#4lE48VEn`JrRn$qwLY8PP3C?_oDEa}W4bI@Q0<Zv(wk4H3Lr|04KF-Lx%-A%SiN)Q5>H+LkV;s;YYCm4$<I'
    'wk(Apo$o~xU%m8Jta!=VgHN$GcC6RvC!9(tF4ZK6k6r~FqMM@vS2#&5-TkVp1j0G0I8r!MLW(A?<&w$XJOnpN!Qd<+4_*vDLUDCA'
    'M$JI7)`ak<a2$)+f|f%^ttyEs_e7bURk&5eAn`c#p8~$IIHcv|tSh~4{G|Efi}fYZ`@&MOit0!DmhSXuRT8=*dXuG)K)TiV1FLs5'
    'voL-vsz4h@`voXk52Y(e*`e^C1uhH>zNq;$NY}qB$lclqxE3V+xbz{^`&HT3SC(56&f|QO&*w*Wl$kvd^x>g3Qn$g_&AD7Hn|s~w'
    'QGA$Bx&QXgS8wk_F0Qn8W>nG*Z8TYH`qV2Wg<Q1+I>b~0<0~d3-~$Vc8ydNwq|FW6<K^kH7TWEO$=+w37T77r7Y;2{#l3aeT^`;t'
    'NZRPw3{mspr-jF!d=Q%|H%MHc#USgICxSkY`7m<sHYDr^|5OG}JNE{SiRV0qD-;eSIq58NaWtXv2TyI=dJ)pMS{XLi?S1@TW>b?U'
)
)).decode("utf-8"))

_V50_PLANNER = build_sparse_planner(_V50_ACTIONS, PlannerConfig())
_V56_PLANNER = build_sparse_planner(_V56_ACTIONS, PlannerConfig())

_selected_route = None
CLEARANCE_STEP = 629

# =============================================================================
# Day-6 Milk Sink Cow Swap Logic
# =============================================================================
_MILK_SINKS = frozenset(("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
_WOOL_SINKS = frozenset(("YARN_STORE",))

def _milk_swap_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if obs.get("day") != 6:
        return action
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    if not (any(s in _MILK_SINKS for s in shops) and not any(s in _WOOL_SINKS for s in shops)):
        return action

    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    out = None
    hour = obs.get("hour")

    if hour == 6:
        orders = list(action.get("market") or [])
        for i, order in enumerate(orders):
            if (isinstance(order, list) and len(order) >= 3
                    and order[0] == "BUY_ANIMAL" and order[1] == "SHEEP"
                    and int(order[2]) >= 2):
                out = copy.deepcopy(action)
                out["market"][i][2] = int(order[2]) - 1
                out["market"].insert(i + 1, ["BUY_ANIMAL", "COW", 1])
                return out
        return action

    if int(shed.get("COW", 0) or 0) > 0:
        actors = [action.get("farmer")] + list(action.get("hands") or [])
        for ai, a in enumerate(actors):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "SHEEP":
                out = out or copy.deepcopy(action)
                new = list(a)
                new[1] = "COW"
                if ai == 0: out["farmer"] = new
                else: out["hands"][ai - 1] = new
                break

    for hi, h_inv in enumerate(invs):
        if int(h_inv.get("COW", 0) or 0) > 0:
            act = action.get("farmer") if hi == 0 else (action.get("hands") or [])[hi - 1]
            if isinstance(act, list) and len(act) > 1 and act[0] == "PLACE" and act[1] == "SHEEP":
                out = out or copy.deepcopy(action)
                new = list(act)
                new[1] = "COW"
                if hi == 0: out["farmer"] = new
                else: out["hands"][hi - 1] = new

    return out if out is not None else action


# =============================================================================
# Late Yarn Store Goose -> Sheep Pivot (Step 216+)
# =============================================================================
def _late_yarn_pivot(obs, action, step):
    if step < 216:
        return action
    shops = (obs.get("town") or {}).get("unlocked_shops", [])
    if "YARN_STORE" not in shops:
        return action

    out = None
    orders = list(action.get("market") or [])
    modified_orders = False
    for i, order in enumerate(orders):
        if isinstance(order, list) and len(order) >= 2 and order[0] == "BUY_ANIMAL" and order[1] == "GOOSE":
            orders[i] = ["BUY_ANIMAL", "SHEEP", order[2] if len(order) > 2 else 1]
            modified_orders = True

    if modified_orders:
        out = copy.deepcopy(action)
        out["market"] = orders

    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []

    # If shed has SHEEP but action tries to PICKUP GOOSE, switch to SHEEP
    if int(shed.get("SHEEP", 0) or 0) > 0:
        base = out or action
        actors = [base.get("farmer")] + list(base.get("hands") or [])
        for ai, a in enumerate(actors):
            if isinstance(a, list) and len(a) > 1 and a[0] == "PICKUP" and a[1] == "GOOSE":
                out = out or copy.deepcopy(action)
                new = list(a)
                new[1] = "SHEEP"
                if ai == 0: out["farmer"] = new
                else: out["hands"][ai - 1] = new
                break

    # If worker holds SHEEP but action tries to PLACE GOOSE, switch to SHEEP
    base = out or action
    for hi, h_inv in enumerate(invs):
        if int((h_inv or {}).get("SHEEP", 0) or 0) > 0:
            act = base.get("farmer") if hi == 0 else (base.get("hands") or [])[hi - 1]
            if isinstance(act, list) and len(act) > 1 and act[0] == "PLACE" and act[1] == "GOOSE":
                out = out or copy.deepcopy(action)
                new = list(act)
                new[1] = "SHEEP"
                if hi == 0: out["farmer"] = new
                else: out["hands"][hi - 1] = new

    return out if out is not None else action


# =============================================================================
# V92 Day-23 Hour-23 Shed Capacity Overflow Guard
# =============================================================================
GUARD_DAY = 23
GUARD_HOUR = 23
SHED_CAPACITY = 100
HARVEST_ALLOWANCE = 6
MIN_FERT_RESERVE = 4
MAX_FERT_BUY = 12

def _v92_shed_total(private):
    shed = private.get("shed") or {}
    return sum(int(v or 0) for v in shed.values())

def _v92_carried_total(private):
    total = 0
    for inv in private.get("inventories") or []:
        if isinstance(inv, dict):
            total += sum(int(v or 0) for v in inv.values())
    return total

def _v92_buy_units(orders, item):
    total = 0
    for o in orders:
        if len(o) > 2 and o[0] == "BUY_PRODUCT" and o[1] == item:
            total += int(o[2] or 0)
    return total

def _v92_apply(obs, action):
    if not isinstance(obs, dict) or not isinstance(action, dict):
        return action
    if int(obs.get("day", 0) or 0) != GUARD_DAY or int(obs.get("hour", 0) or 0) != GUARD_HOUR:
        return action

    seat = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    private = obs.get("private") or {}

    orders = list(action.get("market") or [])
    wheat_buys = _v92_buy_units(orders, "WHEAT")
    fert_buys = _v92_buy_units(orders, "FERTILIZER")
    if wheat_buys <= 0 and fert_buys <= 0:
        return action

    shed_now = _v92_shed_total(private)
    carried_now = _v92_carried_total(private)
    projected = shed_now + carried_now + wheat_buys + fert_buys + HARVEST_ALLOWANCE
    if projected <= SHED_CAPACITY:
        return action

    shed = private.get("shed") or {}
    shed_wheat = int(shed.get("WHEAT", 0) or 0)
    wheat_keep = min(wheat_buys, max(0, min(shed_wheat, wheat_buys)))
    fert_keep = min(fert_buys, MIN_FERT_RESERVE)

    new_wheat = wheat_buys
    new_fert = min(fert_buys, MAX_FERT_BUY)
    if new_fert < fert_keep:
        new_fert = fert_keep

    def projected_func(wheat_qty, fert_qty):
        return shed_now + carried_now + wheat_qty + fert_qty + HARVEST_ALLOWANCE

    guard_passes = 0
    while projected_func(new_wheat, new_fert) > SHED_CAPACITY and guard_passes < 32:
        guard_passes += 1
        if new_fert > fert_keep:
            new_fert -= 1
        elif new_wheat > wheat_keep:
            new_wheat -= 1
        else:
            break

    if new_wheat == wheat_buys and new_fert == fert_buys:
        return action

    new_orders = []
    for order in orders:
        if len(order) > 2 and order[0] == "BUY_PRODUCT" and order[1] == "FERTILIZER":
            if new_fert > 0:
                new_orders.append(["BUY_PRODUCT", "FERTILIZER", new_fert])
        elif len(order) > 2 and order[0] == "BUY_PRODUCT" and order[1] == "WHEAT":
            if new_wheat > 0:
                new_orders.append(["BUY_PRODUCT", "WHEAT", new_wheat])
        else:
            new_orders.append(list(order))

    action = copy.deepcopy(action)
    action["market"] = new_orders
    return action


# =============================================================================
# Step 717-718 Terminal Harvest Rush & Shed Drop
# =============================================================================
def _terminal_rush(obs, action, step):
    if step not in (717, 718):
        return action
    player = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = obs.get("farms", []) or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private", {}) or {}
    tiles = farm.get("tiles", []) or []
    if not tiles:
        return action
    access = _shed_access(len(tiles))
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands", []) or [])]
    inventories = list(private.get("inventories", []) or [])
    inventories.extend({} for _ in range(max(0, len(positions) - len(inventories))))
    unit_actions = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]

    for index, (raw_position, inventory) in enumerate(zip(positions, inventories)):
        if not isinstance(raw_position, (list, tuple)) or len(raw_position) < 2:
            continue
        position = (int(raw_position[0]), int(raw_position[1]))
        load = sum(max(0, int(value or 0)) for value in (inventory or {}).values())
        x, y = position
        tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else None
        distance = min(abs(x - sx) + abs(y - sy) for sx, sy in access)
        replacement = None
        if load > 0 and position in access:
            replacement = ["DROP"]
        elif step == 717 and load > 0 and distance == 1:
            replacement = _move_toward(position, access, tiles)
        elif (
            step == 717
            and load == 0
            and position in access
            and isinstance(tile, dict)
            and int(tile.get("yield_units", 0) or 0) > 0
        ):
            replacement = ["HARVEST"]
        if replacement is not None:
            unit_actions[index] = replacement

    action = copy.deepcopy(action)
    action["farmer"] = unit_actions[0]
    action["hands"] = unit_actions[1:]
    return action


# =============================================================================
# Agent Main Entrypoint
# =============================================================================
def agent(obs, configuration=None):
    global _selected_route
    try:
        # Step normalization: Seat 1 in Kaggle Environments lacks 'step' attribute
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]

        if step == 0:
            _selected_route = None

        shops = (obs.get("town") or {}).get("unlocked_shops", [])

        # Locked route selection:
        # Structural divergence happens at step 150 (Day 7 Hour 6).
        # We check town shops by Day 6 Hour 0 (step 144).
        if _selected_route is None:
            if "YARN_STORE" in shops:
                _selected_route = "v50"
            elif step >= 144:
                _selected_route = "v56"

        if _selected_route == "v50":
            action = _V50_PLANNER(obs, configuration)
            action = _milk_swap_apply(obs, action)
            action = _v92_apply(obs, action)
        else:
            action = _V56_PLANNER(obs, configuration)
            action = _milk_swap_apply(obs, action)
            action = _late_yarn_pivot(obs, action, step)
            action = _v92_apply(obs, action)

        # Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # Step 629 Early Continuous Shed Clearance
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # Step 717-718 Terminal Harvest Rush & Shed Drop
        action = _terminal_rush(obs, action, step)

        # Late-collision terminal overlay
        return apply_overlay(obs, action, "late_collision")

    except Exception:
        seat = 1 if int((obs.get("player") or 0)) == 1 else 0
        farms = list(obs.get("farms") or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (farm.get("hands") or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
