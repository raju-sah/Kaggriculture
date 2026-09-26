"""v57: online price trends, demand-aware livestock, compact market orders, and terminal delivery.
Farm route adapted from the public Lizs replay; bundled legacy helpers retain their attribution.
Validated only for the standard 720-step Kaggriculture configuration.
"""

import base64
import json
import sys
import types
import zlib


def _lizs_package(name):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = "<bundled-package:" + name + ">"
        module.__package__ = name
        module.__path__ = []
        sys.modules[name] = module
    return module


def _lizs_load(name, source):
    parent, _, child = name.rpartition(".")
    if parent:
        _lizs_package(parent)
    module = types.ModuleType(name)
    module.__file__ = "<bundled:" + name + ">"
    module.__package__ = parent
    sys.modules[name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    if parent:
        setattr(sys.modules[parent], child, module)
    return module


_LIZS_MODULES = json.loads(zlib.decompress(base64.b85decode('c-rlKiFO-DlHjkD<(=1n1VA9=tJ#L%&=PIySu(YhJiR?69#jMhWR1Wo7*&u&YxM6MM;?(!6#&Yf+3AI6+9oP9Bd^HF$T&aTtEQ`bSyzL%hX<2YxvsOxO?FeRZYNciuBO-bj*@%xRe6(4Ci8W@US*R>lHV-LRh^_oQPydlmqm3^sBhD9d3#a3IDYvu86_Vs?#<KHO}4rKDCZaV@bksJaWA>JcbyiqiayiNn{@RitNHiGi(;0|lU24{q_>l0xyYxtopeh5bdN5I1pdJas-(O$U-6%+&X&;iO<r_v()XQVFUgA<D-Eu)x^r<4%P;Qrl3_O~SMcv{FIi-TfuHn~gRX_P%3#U`&1x{qvL*hZ>z*U1F+#z4sYa>+kL{v>j_$oZ`0J$3RxqM;fvb5z|95&>WvjQedi}Ck+$Oq8QohYrF!L%|SJ^DNgp%tl0U$|wxuE(9@66z$xF}vh87%!GyU7aPizKgb%J36@qzizY!+I_=_*YRU<s7!{RxNH)uhMBYNRp?paVbE1w@R1L)i=E)O{VMB3R?7UvN}y}vRRqWdN|n>HvKwVCCl|C%n_ERs8{78d6(DMfIZ2ZqI{PZS2*a4qFgS^0=vzz^Sr*rG4ldIZ`+`ihgj;zO<G@L*+ud4<k_?1@1LE(mUnmuF7Ca2b$0ys?@!Lo{(&2Paqs!bv(sPHpHH9t%zyp;^z<43b@Jnn@P}^v>h$^Xt5Ys{e0+9x`byRR>Eu}b`NPTCtEbPN{`<)pwS%31ad!IT*T=6W-~VHB{L9nl$Ilq~AD{jmQCfEU@~4xN7yQwV;K$R`mnZy@1_LMH$7jF3n*9Cb>5o6XB3O~B9VLf@p&7TD<Wcfy@Rj{Y{kj#oTda3zzEQ77$-&^uU>)%5BlA_S2!0hHd2QT}a+P!mOzipb|CyYgJvli;0&y^e9sKF!$>j0zi{r;nU;Tr=4S8$vj8BU7&1JUgyiFJDtcS-wT`%g<a4^(ozFyrP$@5x4IY5~&%CzQY>SSi`r`fVjI<Ib**~w~Eu6oJ8VKM#PJqpge>dQIS3Vc2%3>@UuJTLM(>+tt(k}aytHZ+r{uCv)Boldi=>RguTYBs6z-!t9kb-I|th;2dg@L_W3^!ve%u0z#<O7#-`SGVUCw-niy4XyO&k9Pd&BEKpoM6ng^143Y_E+6RUX+6CrQnkq6W(n4YGrNYfuPMVSyGfTzMH>>>ntYblK;f3FY@WX#Xu5zP;jrgWGKvyjBtjoPs$E4g2E+)^26x3J^;{;2eKNv|v`a&7kM~mr&220Cf{o6{)ara}Ya(J{@i~JYW1ngS-_kWgr3w!|eAI}y%%(L>2dhvWH3!wDx(r2^U5y%0fbH_C?(m|xP2B1*8tj3}x-cT$vp{Yt8)Wa{ewcO6?VX&=0T7U2!11)W$~tDyeF3toJK~|7+v|NC9i%ShQJTJdAZjiM<D7t$s~N1Q+lB_n1u#fza(<*oIUai;H9z6O^q{z-)ot{ej-4aORqdfzuFC(QzUg!$*1@Go`01XD7hDfk@e1ztCugTG9=>>X{P+aO#ImgN8k)Vk&f(}}@3SdzU&&<#W6bD`@Q9p~@jn3Hm#ZB3n#}1$eZy`5?HT)ZZMBZ}n!|tIWVc6&VBm<7D~`?9!rg?Ly@ZQlOK17C?x@~0#|Qi4ble>P&AzERT|?>U@Dy)>M=4i%W=@<7M^uQNRoYEtS`g)MUA#j8EnqIgF)*C>JEA;t_|*<5J`>^bpCLqhJ`k!?%cBqqW}Po+eqsRhDS`mvLSo8A6{*U>P>&GrG$?Mm;_$TSjY2l`eJ@$VjX6=295yV28$MgXD*G(HB52eq`Hn|m)|f`&6p7uD5SS_e?^&!f`&Gk%ksFZb1a9nf4vZ+U(|J+VX)(=A_r0Wp_|Z%1HE`Zt8jKts(%!?3gMhWTg#jRT>xSoq9?qA8an~7A2b*<yWQE=U=pR3HhRL@h0Q#-mF1(28`+NEQ{C3>kyiT7dFLRhUY|>R;WXK5~4!-UsxY?4F0sB)f-U40;+V$-8@y{nu`q-I-ceMuGfEUNB>s6K|Q`oW<kVOR8S94(uz09D;WKmAv;2Q|IhZNveP_~fJn5g3J%#g3JM-cH1Mgdf*Tq1Vi$3ffH3asqW;qU526(t+jOC#Z}OU$+>Xe~rdAh<%+C^ZulP0dtH0PqX1go}H)dBB#t9qSv3kWx(~1fDG#U=l7|+#`fTJQH=gcuM^ffsmmq3F=_%RzX~VDjH+Y-+SdLJP6apq^eizDLx{-XBW`MSHGT}1TQb=yLfy(KE+k}NOTcL=WPt0KKDy>4DkL&y!i!QzOmXfiFP=%9_?>8UKcAUI{gNA9qBnNw%=#G?ZrK=2YaH(g?k$DAD;%q@j85H*~ijv>#XAI8_`<s<{{iCiY4`N;SsY82QI*^pJ?qP6?ojCee6kbkQp&iT8-v<%aM2Lc6$!KSJ}pcPxl)&|81R;q=U|_8i?0?RhEeOYCP`yx1Ut&n~q_M21Enk{P{#efu?o$WL;(iTE2z-g{W*GMAp^xe~yzvCfbfju2k~Cf^p?vy1HeUwJc}?OnX@Y(sqJ3<OvY?8)O~d!V$TIqi<wl)q1&H+?uDP7AN5pHM<EX3Rt!O9$wkVxir6g02?WIX2B{WAq?J!v>r&jaAA*<;b3Sm3h_t_xjtHEYE{0Y7mVrIc~FKd-I0r{L|E~$hhXNCBEc7Z0n#YX;lubSz#i}V6m)FsV>(@xD5(V^))7<=zcOJ4TGt)GzGtgWh`rPp*+;c_kzRGtIo2H~5BS8PAj*i9M8CIrwwO(jPF0K*{)uB+8V*>~*!CgAftUfUhUS5+kl-+saGt7N+w@cwnjy>%&Lk0oyUr6j71ih23Vs1AznY|P(|nP_vBY*iq<|dVwqdyvKs`E#O6a;mRK`+ecsyJcDc)>!Y;->)PpTph#bNLyq{HEk&XM6t(XJHvHpz~CP{d;hwnA_cJ)gs1wt|GnCnrxFVD1xC9_&y`^grTI<2dGsV!Q$3ILmXQSeXb^=6StCMgZH-mzsfLnHg0g9aua%r^<|&@p_l5EPdl(tU#&lWqG}gjn)OfbS7|j&sK1KH$$K&XGhHd5Pd8$zA9I6=c>}KZq~KuYr25jVlvCs4vQOj`^(O~&)k=;S|*mhqsU|qTgJtUY>wnFe!?q!`Kp!9uddrFng?;XCFy0=!EW$L(q}*xF8=cX7|;8*+JUWh;8sH>46CJ3;gY3>X)n3NHU2$ca_hr!Pc;Tcw;L?A=3OQ%#gh_3Xt!QuBRC!90!}4-!DYVRW3}8g8@*bsGnX}bnJpGc_BMm3rInZ|%Kx`ydR><I)<wZ4K7>iLR<ec>`KXXLQUaJ!qi~<A(Mx~SChRmaziGw{w?!Z=P<2FaMjkk2VrGj1ZYa(%>S}<)Fjcj>T4Lu&z<hzO*AmXz8}}}u^#fEmV$qVv-n0112#>Ac${UL-uMzZ=nrb?%U&%@?O>ZLn#$(WLYUKR%mVMO1G$7t26dViLn#U=MBWa!kBPo8seRNrQUlajjH%-4CCBw}^HQduA!e#Mhi{1|4Q35r*-tbKDtcfrO;)!Zn5?XLS_s!@$(S!w~_oWe1-@yejK-?I;l=#Tee-8)=ST@l9MAThG1O^>u(lk=bT^IzyApGZkBDBGB8KHWtHZ4%BfRvVt^6Fq|9*G_RY5D+IHb|FfIMC_Pbb3iYwh%q<<*TPa0PsfYtdMY3imWNZ0`!cK_*^5o4@Rk^diek0(;9)>`$*AEu?I>7;c9}Y)AJ*%f*uDq7q`<VEnNTyFuRRY370%ry5LfSKaUs$J=64D={W-R$rFONOW@(HV0jb>JzXPm<~2F;MK?|-8gY0+-b0E34APk@x0i2p*F4aX{R{R^Jtl6-x7nmF-=(XWklokm3eFJRU@Rb46H(H5UCp2t&RVqy`5dc%QQ8%%s6;ZRA7IW#i}dDlmI8PnzDEi17W6l>D({iV*l)y_+`_@qKlNWj!)VknUZUyTi+UfS92}ME@_NAc9E$$mi{aaf=7i(p<Rv|b-m{H>ImZm(yUhSjjx~S>0RU7=+-?H!%jwyxp9lhO2AVH85Wd?C;pOSC0>T3eAy8w9^P@Ecy`+F<1<@A^-91pGNhxqW38GQ16u0sd3#^OV@p<unoP36dm-QjRRiqKg48lceiC`M7Z-6PP^WTxNGj?VCpm%vpG*5Gx$WtK0t9%BGA{v}w6Qg6SuT!!CV;u{0pDJq(;s7si*{<&EgKzG_MZ&sKb45WqUmtwkLs${38-0fVDRtdDC|@<@!Q%E+itAu4qW@{?=}%Rdi(+k%^5LUzhoV?kPx;#qRK7-xB{U6xoaQ`GVs}>QyNSJ0j2@xuz6|iKXolTOoB<!TsUuzRac#4#vz^9SsJ%OQoFoLRdUn1Zj3q}3&w6|g;_J9Ul}U?aq%a+;5LM4Vqt6KR;O@;E*Zvs_ytR&-kE^ST)8Y?xPvgCdcV1;~VZ3{)Tb@e=!>ewsuH7*XCa&{_1^;dz$a~>peFx*h(V3+;fP#xa0z20#+OhY#Ve{q@P|vTKYm}YXi2*5Wh2Ov$@yIl1<aO;mWyDB)LAe?h6b{3pa3#Vz+h|Cs9$;UaY+Kz7-^p=wH!b{6$7laWtdMI9BI^kiuLn(%AFZYz$+qTcp;=vNLg%y|j=h?~PR^-#aMaERr>HxdD6?|r5iZjzGv*FA<;;^d9h0^VW|tJ{4c!06@?0z6rZAQ(ZOVyO<4fcc0I0Hjcen&?lE0NXehXva4BFu?a0ZA^AK*gO9FcwfqvY6pR<Z@>n-If&4Bn79@?AJCm*t@Y@{LRD#b~F8!wGY*-jM9*KYAEuM%5}{l+q6?S7fb?cdltT^uY8N>5e^{C3eJ_n|l@8aL1k<dFsaAc?$ruvx(DCe<N9W18%VW(GNJ5K5M+!D>xJt@IpwKuJaZAH6>RD^lMnb>4Wo8yn#`@V+*L`+J{EQ(`i*JQ&5uJD)A=bl9>@!yrHAW5@8>X6%eCDfWRQK;?bKf)?_JF!LjCX3p1{&E~jq>f6mH#d+skfEgBt|??%a2-wb1?@Gc{e2p=7SzsLSS=yybGg3QL@pE1e?8jdtp`$F-5T)M66ELl7sds&6IfbgJF(2R(g+bD?a$7CGE_Wn$Jf2O@Z)83zH@6WXNXWIKS?fsed{!Dv+roBJY-k)jj&$Rbv+WRx@{h9XuOnZN(y+705pK0&UwD)J)`!ntRnfCrndw-_AKhxfyY46Xp_h;JsGwuDE_Wn$Jf2O@Z)83zH@6WXNXWIKS?fsed{!Dv+roBJY-k)jj&$Rbv+WRx@{h9XuOnZN(y+705pXtBKpXu;WO>P314Fg4|rq4fnxUN<YFZ1GIR=iD?w{TAskF>YXDT;aeRXW!Q-RG9td&n5<B>+76Ila1C<<s?o%&Dq+J-ao&PRi@(?cu@TAW5(AGDg`goI3O)KsF&mzXP?%d`MC<7w^AY<u$xAE()V!U?D9%*srr9L7oU-!l+6?SsRPK;7dtEo3BcCpu!*15}mH#l~<?}`rA5NXJpt2%mJ(=N}=)C!*jcW-C5+9^dx|5wYo_c3wTwMmM&Y(VI9^f3GOb6`^oFqyfl+)QP$P#*L>9i40aNuuF1Qr!l7s)&*P;ge{-PFpaIIdqN!zc^3}xAtdi#p10o2<g0m<KlJzpQBFo9;iw@6pm7!P!v6mW?Q<xqk_F(Og(ASI?(d?gcj!{DV>3W59F<YR<8Yw4C2u6)J=?qp(ImW>TGwzY|$6UFV&FA?vPZu7xu!*WBo6B?s(}hK@U}t{LGV(sjYqTqcmayn0)O-Wa(*g&c;ag=*)<%~%c|{16uIe0j$akW9{rU~`3;Y0Jdk$-itR3vuAMW4w;_T_;lgSUyPEXGg(o;V_KKuFP)#SzT+41w2(lyLDVRa6_?4cLc5SXnm@L#}X{k9@K+;H#>U2o+T|2phOJi9uNMEftP{WYu`-RPv(k?_9mMm)wkUkwd}!=VddIQYVa@Rfz&dbf2B4lS4ie<EMgMDij_S3EEQ$N0j*Qdkg=7=)cX1H>PXWNYON*O5&h9mXaRTSx73*EtZ2aBz6&O}b_D+Ci^#IF$4MvU%{Ld)Mo(b1)2c!uG0XAwP84OV5bVkxN(3cVv^SJ@D}9qc0g(v7ue{JhKsXqfjaF{t}#f_d#h|*Q;2+UB{~~U1lA8pd6vOh_aVHV&elKA#lX?ujD`Jt)^b--K75=e^=wvMkmH@N_r1kh90|8yn|Y@hWSNW;8r!%PVTp~LWBw1ks=QZ9S=u$h~-sdOI884H9Z)%HXbS+W+Mo7QrveB?FiC&+6$De(1(a}Ib2Nqrzlr&b>_d5Ndhn3LxvHIR8)PCd;?>>Z#P$z^+|`C+`n)9Ez=w>e`|EynWJ$I`ZO1Y6-Ts7KHywGTYV(+79*Kwu88io4x4fkVj3wJ8Wz-qey9eLFYYrQH(o>03r*jfzpcwUW3@$*34enHTwV+3)s3&^UXuN`&fz9q<?9=DBzk<`!nIUP_1~;S0zUN;#X?-de;bXKkp4JV5L*Zv>lfp-qX+h_9D-z+fq%+@wZn5K2LU@pa)gKafXmUU3DAGKq2&QJd>}yI*FZcarvNEN2k2nN-SZL4JR%%bznq1$VE!!R%5F1@{^nUokaoTMku48qVb1gWj$km9_!rpH8QW}-P+cQ;UQO^hsddzV!<S{bIBK%R3RT^%6kDuesQh*do3-F>je{{h=^gA0tg<w7jSMh9g6w?cm0+AV-`|?I32)FWy@7WJyzO;(27axxFbs$rapFKQ2Kp^UF9J6r!yFzcXv9<77Yz@rkB=Dyg`Tae9Jxw0Aj4JPPdX|zgCYif_1|<3j4qFX=fr^>GG$a>G2d+OJK$n3GwLf{Eplk8g?sRjLTwDqs8nWT?9`<#vi?%J>MuvkU*$JIsnQ}V*Ohw54&<Ub3N9C`nk@<Y(v(nn4xx>xXF%XOsl-j6xQVsd+chx2P+Kt@(=+0d2$`ZrZ?3xQRyW|9*v1q^{bQA7o!2H}L8puW7&#`gKb$tT7xYcp5Fu}<WUp>}Mk*ai!L9<q;odcn;NI(nqhP(&(77m31heuw+6ETT_`ujmqKhe%*S<TizU<uLD$}_ZGIv~mZWCJ~7L=gtalu;RLu|0CGiEr0Dy!9{-lUjpt}d0b9xkfto&}@?<(b!z;#Qjmxs%Y?=II~VgnS%{jA7StmC-SaO2JT!K%7y6^jwNNtWCJ)irBcx5pz`NFi+Bz3@MY=LU2taJ;1`%EJ#?miU_lVv0e7ok(MP~Fk!wn(RP?3jz-h<(o6bEbL=7ymv*<cG>sdWN(#zFuBEmaY=gD7-aBVvjh1_OLlFm#P6R+krPqRKJ$6+yqj00;)1b!Lm52`bXNP;}`cYl{untA`o-84$Z8uyB##3HJ$4-u+jH6OvDK>KkNkNZjyBi_K@3irTd8qY#pn8b1nQhM!b<%haAMoG$S<-SmNu2Bmaap@2Ma!FxXq{oysaiQZ-@Aeb5$<ckf*QmG?Am@(1I=dQyRm7ekQ!DTE#@9-59M{+pg;6faQ^$!4E@}U+xG)0SNRpW9(vS5EEA2?>u`P3@vzWA6b;oODKY10IYPOX{xA(mixFJin-T8Epa<JRT|`jzvr%;TjpRhz9g#j*B8&Okbs43Kp{n6s218qA%QRov=xI-t189GaVFa)Wi;0yQhN~-Qr1#mZ504tS^zp*L$Z6ac+8uq8uvRsa@!d=_tF{)r1)3_5ZB@@$LBzvY-61rDeu1^xmUX2Qz2<wL;&r1K-)(tdYtJaBhtcGmbD}I1dP;u@KP@z>t)9EaltH^PlZygs)A3}p`IoHMCF9Vs!(PuBJd<(FPlY3Q?_Ump*J2zNja;O|GRfAVotz&&NOa5Li)g%KJMwR3^d@GqWX}%m7N^4K1KlOp?nJi}T*zwl4emm@oRkI7h<bWGa$Gq1AiN?)VKPqvb1>{izL-4(5JlZDi$0w)*q9P(T%wQwe)72zN6)-^k87cZgBK`2AbFxsp8kjmnNyZ`;XR(vBIOt)tR{m(ETA{@Ona7V?vYe=JTqmsN<jZoAw&2!$493;^V$@UT)6bO86vx<kVXk9AB^ZZ-{ZOsiWb=CYF(uBIqTGU3K))L4QsKUq9aZCyp>Du-d?iASSQ!YX#2zP2rwF+W%!?uv3s_#KB(fxm7mSBN6KdTmBx^;5ZC^;t(XShSdL<ZTgI)}u(J2doNgJ5ERkB5w-aLujis;{p7&FWruz<tM$Gf3_1&$E@t-Rae5-9dM|fiyrsg=QmMO5&d|ZH4OVOYZA6a#d;uFTPDZFX`y=r}j(4j#c?KE|x-lW>JlWnrJcxs-nD%FbgrYsM_I2cOAG|Q%JdLUqtUjeGEQLD?xiQ(Y$n0ii9RIX1KSz7QsG2~&60(9#BZxR}@u<wvpef=8i0{z0BewzUWd;J<k|D;!i7n@SL!&9z=ryMKtDFmqnRsj(zYLu4YC@$0K8x%(&J#-`aG}tA2riZXdb}-r!9mg0{BLLr0nL-0J%9&^c>K}BQjR_SZd~n(vsq4@7FHW}|w#6NQ5RPmMo>g<a7(en0<k!?5h_Q^hFfwepR|DK`$HzJbX+*tU6cH;JX}0HHeS&pXHo?-CPnzv>*uECqeXor%;O8~O#Xy{HHs0UHEPi`)_&?V8yrBc$p=1>7nA`=r>hPB8IZQFe)6zb&Z!;a($;V(0ss_iWfurIjL^8?T96H$qfdrh$Y;sXzF8^vg%W~OKqb4P7SW%vU_-)eU%pZ?cfMR^cVPGc(AbfJw>B@cFXdd$_YF*uI`Wx_@q8G#9+#7G0u6H%>HcuG#A!=E1?BC+`^}u0IqVazeCpFs0)w8o0<3cnfgTr(Z-H$HR$aLBev|(#B2~fr5OWFcH#MiHRbM=rnZJx_G?TDq@%zOKz5fwFdq$>;KWV<JebEdnYwQk9RBSSO{O~8v;lMwvfk5CV8pBI|isX%-}Fs%pah3eCvw~kg~SWSLxQ)6RyFMVK5J?+AFaqs(IpFVpsaRR-(cy|2Dt9V?KhL~#X;Sv=L>=2zLQNdrlKyl=E$RTHrcEdLPG!3E{GLx>TqvC5~H7sR2@+hFeFR$IlZTu+EE#~Qu0bQ2ZFJC{ggC^@buc26F6L3hja-S&USPS9KNml@Vqs<Y%rbBggMts&=Ttd8nj+HMbh(O!uHX@CL8~r%Bs(N^}iSu+7?*%M>x)t3EVnk*I9p_`W*(mw#;iCbu&XcT|ma}XX&9H#leYDs`L(Zy3f_4S(A!^4?Ui>_pF3KvK^%rHiG>@g-WrS1<(J)h6q^dn;dtX&yme%PM*lD!ORTa!9Ri(aVdsQwyE^f6+C<PFEDN`Qk$X32JXPDL?nk2z9oODegJ<~?dPBChE$XOA-KYn>KA^Vc3o$BG25#!TGu?z%X4I4~E(LyvZ`b3*g&z4hs(e{}KUxg_V&_c2yeZf$rFL?RW>5GZj0W+=dkAFT<cB^{b>}0Kd=8LEQ{_n>Vgrch2)DSWZS<vqLvtNIC{L|#+3uU7l_Tfh_vu*!zeD=%a<*U=P6V+7hoUMT-K#$K(j-Shs1)<Pv?u=koC$A=tkAKkc4fYAs-sh*MuYP)Zvbh6c%X)nF{N(KAge`jX*msNJrtDcc(w^S9PtMMvMX|;@_6Uz>kAu;X$>0AwcCss=bvGGmG;bzw=g;%2HD5s;=NHX@%%EWWdca7p-jWUsAAC3(rww_mmG6qj8CJv)RZmq5GHO2LSmB56sF5GOOc%HYnlV(ppc?E8zR)i2VQA;+t)pK+Vp&h-8ASuDh+jHV3=j+(|2U_$CnJ!tA2U#q-%c23$}182>{ew;bM(DGC9)oJb;=vs<@2Hp$efEOAMoEF8@L+|z!?PJYzllC33?e1%o&}N9u`)Ze87KyY<>zg#O~~E>G2y5iwE2~Fcnn!1OK;Wa5k2wOIDf#d2S5m*%;9C6Q{i~lIPALJe%^;+`s>UP4T7eJRJ=D-18$dYVp&@o&#b|&sXYwLhwE!;oSt%gwl!tHT<szqosk(^0uziT!dt70I?~0qYDq6iEk||0Y{bC{R~s_RM&8LX4wr4dIC?0$t=C?=(rbZ5Ll%;qK7e(!?6N#U;P(akQI7QZzSFhd}%3l6Y9b=aH^UhUGC|CfG_|}v302~oYFnu6+5mM$QZT|Yi6|{EAv(uLm$SF@O*oWImi*u*2_gcrJ&E(6b6{dYULPvaVxy)^|3Q?mGuDz)X}V*iO@2AL+?Gg2+2cz44v7F>p~5~-vnvfO+6xLhl8Y@$I89LiHSjGY)i7r#dy)mkV`|6TBrl}77|m_wSy@CxGoNn;aT4oy&8ta+fwblA>%N4HRux0HQ&L)V|nBAs1F^C*|6+h7hR{Vvs4Egd+yNS5InLQN)~k}z8$D<2V#FC2;;i8=n5oqah?tv7vEWe`{Aq{g3Ilh9{j6$FLr>r`#mePl^%UdUg~%5OMK=Y*-#90EL~!t`?yK-0wb-_K8O<5gF00W*|2m0T9An-AMC+kFcvgJ1>_YcAApVJQMEM3rw-CIb0VB+TI;cia#JPXS{sX$k$Y1)hFNMX%d%OtPpiA0FH*t8R@q|SMiFU1>pGOgX^pnNM-b3}O=kRxu%=!;_!3t0w%=>wm4?mpY9bDs*EV_}BO}#>oe8LW<MIsgyAA+VWwre3T(loux~M6%Lw&u&3G0k}Aff9A{P#zen#l#Ws4Pf#kdvyNUWmRF=Ibje?9e?L1Gc@Vy1kI$Q$WoLX@Tn>rVWs_Z&C<B1a~#ft>DK{x`v@rYk!!L_@z#DdVEG3!Icr|yJ45Jwskl0aW}3uP?Cw|SsMXDHI8L2Ib2)21^#lm6?{dtcIbpL6_YP2Ub-UHMu+Bvwe`TeJ(Rpa5B8(#EztdF?p!HJ3`;8*ZHJ}S(cmYnr-(gA)H;0Np?);)g0Y+ClW~w=2F^6q)d^rMAI-wz2}yv_#z4t$LWziU8IInlCP<-{kSN3C&~(TRN=T}BQNPi=;U*{UdH2|aCVaM5>D#0vUJUn<$w{I{9ZzcF0vxkq%;}?fFvhQ98&@fmDY;c^g^{6ilnTEnSH3a+qOuS3cFMO5Gptcqm2T3WFtTx)=xc6Uky}@=PQ?6TWPj`pXN%pr&xsgvI1iFdV!D@5*%#9B48G__-hQp%u;Pns^@JBhEyUp$-RMJ5K@!$PyGatadQfzw?S9hPrHw0~bdPz*H7^`_Do<Fa5&W+w$&JG(jg&Rw*9U*asDd7Y#^-Is|8aoexJUdS@tqK1ME~}_Dz0Qix#F}$Q}IP|ybeDxYL+LMkdH{G7>>uTg;Q@Ed4OIc=a*O0!RwLp%d6?3+Q|DYbFGNKefDScA)2n|D3V7y!siK5RA(E{&REL6aB$37{aGW6WngF@797u!FN4R+Nv^BD4}yw@VQ|nkoBgrVQ>34$`i88p{_N=G_UDZTp>I2!u25~GFE#qNS+({{3?Ierjrvwyp*uM|617J<2hw`P0gd|gD!;ly2Op$1MPY(5p;x-^n2vgiG?}lV2QsNN{ZnKsZNFck(K`mXVp>-v=|y4ld6&zqU>!Qz>|VmQ|IG%k(m^!Vm(^`WNh>NEKD2|C#L#%jyK4;6g^{D!^L(a7d1Mr%U4UtB6tS9PPr<Os^In=p-ys^)7P@&SMpHyl|D3a&TmK;6L_t^7Ps5)3D*clJKY78AhIa`4<cDAy-XZvt2ji>Z9m78jg9u8)odZA(od{6FT|+=MujrORpjzj!T^J~53UUZL27-!w@k2rViSd@2LlNx*E&YEIXbGqEsiBniA&>SUkN(JzM;zHFV|VUGB(#Z%EKaf>gbGp3;byrd)(w^SeSF@NFahH%6l)vU3rZ<INxBe`NWEAV+`>3I`SD(C<Q1#O3KJ{Hguz`$ny16EL;|w-pyhZTjJT!r<T}-{I#nL|S($MF^>j8%{?|cLrI;6^E=?Q-BbD~jk>QBG3!E=RTo~U#L5)fb+3v1-_Lc?d-a5Vl-BV?GN*b}NF-7wRHS<4#&iK<6l<aJK#%~vGadvZ)&Cn-uqIOO(6xtJ3#wT}*%1aD+oxgRzaulnHdtRL)=jaNfIUdynF>^A#E)n-#I|@q<nzWPF$O2x@Y#m~|>WOeGMfuM8rggOH_jS3-e@84eO4(lA<io?*Mhg#-&5_b-lMDu-Ywm4?mJ&U0&1ZQ<A|_esuV4PLW+5?@P(%~AoI;Ih3?ZrkPug|GYd`DPWnVvtwG7V0G-p^ZIgL1m8g^qcPfIcYXGhsS8-}Z8!gpknJmEuL=QqlGRjm#N9@5mUfLAW@t4?%d^c3gUx^>ijkFnYD{8w2WaUKuFr~a2+C7c@1!ff%n1QW$e$7u&;O?Dl#`aS2q2`<WBa2|SQ3|-IK!1LI4J4TtQ+m28TDK@lgCE+r~*L+^ly%Ju2&gpV*KqV>=S_2Z_VyGU1CoU&>16hv3aKeozuIt5*kzM{v-0CP6&qnY<BfCIOe$UO__*ORTt3_#6P*AhUw51srBRW0TXva$>7-rM73K=<a(!gwhy|uMZ%Yyn>ogs-kut@IJCG!Mmx(Yn6Jrei5PMkZ|p^`G>rhj>kSZry&J9(s?0jZkqM@O)$@7Dk(90#|VXyxC(BTEi~O8Ur;%qoQGt1q)k-O0MPcPo>BYV@Lgm)Fzl$+WEM*e!Se{+oC3imCKPB=~pY`RFfa-N$1uKQjduvXN0t>`5d%ltkhhpGiQn-sUQ91Bni=Gb1Jq!uL+%0W6&&O+cL7k17wiU1LwKJ@k|)4#c)HJab=cs&MF4=sZ$yLqXO(I3Ha_90%6>5JvJmigIT9h8USCm<{#J9b^hwyJAjCRRG3;UU<!82`9zCMQ%?!M(@>%(>XV3Z3pHkxwZNU-W5*T<<ZDnTq0G<=))p(*VoMTF^QRJ)c4jtq7rl8$a)2OG;(|Tf?JFf+$K4<;dRZYBP|P;hHX91I$@j2KC>NVi5p`0J}wL82MEj<niQ*aJroj!CxSB*aeiH`igPOKvL=4aixe*>?cBOuB#$l{$!7i<xNT#5!vkQ;*uyU@D36V?8YGUlF+u4_y1Er=BuvKQ#F0TFrKV2NhieX+go-2`IPKHorQO-@v6nnfIgyd+xiJ}yZYCpf_H;-_sgco|E!`lzTin35o3uIB@T}*U7xfa7Gd9|UD0R>AOIGUG&}G7_w<p~g&d1Vt27gNjfgrG{b?m~MY#+;Z_gJ<S+}uF)*#2y?$cn4_x<jFy98+KNxWJ#|u_u>S4q&QD7*N`|^*Hb>RrRxF@(8TRPX&5mC*vZ)7!CI+&a0~qNDIBQ$ixd@a@$@<TTp)C-S({DY8-*IjlT<(k$Rt{v;SCEbZ^+WxSsisiV>eKme;9b&;okSS&K%EG2CtDJ*tT64jVh7J<K?@5V6?sP3xHmdPCkAihR4^<G$3Ex{F)q%7EQnPxNT+BW@qD8dkT;U?>s-`$59P@Y*&~WL3#-yvBVsER79QOfz<ieODwMpym%%bJSAv0Cmb<;ERjtt&&YpiXj)oLjXS*dQ1xK@%=<8$h-@g@TiONzZLLq7@C^6Mv7^xS(i)A*(r*rJxIm2kCeE|aj8;RE^ya8E_}kPE?>Mb$R;9|z)MHA)`8)4GA<JvBp%fIkBDh46UT2AiaM6XxZ$Y9U0d~`_IT#qNr&8p&=FFWy7^$W$YBFn5v-V5ER%R%aT%>KzPmw8?rr07ZxM@|<7P+WaaU~@CI``00k`iOLc8JGL~A2HWQv;P*{7bgkneYV6Ju}u!!PYCAIJ-EeK!*$VW-x*bedMz6Ls>O_H8Hmd-dFZ{^D_ek-t%i0}btG^rf7^v@KdFCh~h!Mmqh!bt|1s4@JlDG`Y?%b26;LH|sKo2SA@Uf|h~!c8-XTGk_h`u8ddLwN6O5B#BV1<lgBm%AZku&b+h^w3urvE+k0b|N4)IKRrD=i3T^_L~`=2;|{1WMR9Rq>_F^b!>!{Xe(UahD|~hJs??9MK-f0kaG?&jo2BM6o24dpXcXw~rfKfPh0N8(uf0s9Gcg)oeCuL&YuAi@Gw&vd&tg~d&!9Ek^yzE-hG=H7Hpt0*UdyQBR5e%XCD<?H{9~W-4&_(U5uE^{Q7S2CFd|s)_rMBy7Y@*a<?2mF^s`M+H)@ml#Vp+e`a5!d_5Ao<QWZ1O>+0IA3wv>{5VaZ?WPK$5?nUoqiu$Ppc;5wj5)c2*^*PmvY;@Cc+nuR^wBCJ2BEHCfTN6bEx+jvLG``0hDe7J5-e-RD@yKc4)rIDoj?X4z>pM98$fwBm>5+5}7Rj^HR!T`Poo8ik?NThFEh?s;2v<d%uQiNOp`Ro6b0M{A)d}(5wIpG3UUzzahRtNy_g$kM60^8y?35ew*PhiS${iv{dEjuAB+EWJ7>=8Hzke0-Jht>WLutk{mOyHRZxf#wXK54>2`6)9$vzQY?AEV(GEtAxyq-+hulmTR3+PYFc@)*2vwN~HmuX75qJvj!ARJ--g9I#dujqbb;v>;9-p=&Xncjxc0LMg)lUYe~p-xD8y+UKS6<N)51UoI3xz~*(TfvSs-78l|M$meGPI6cH*BFHgD@P>6)m4yV3|TK%fP&Y{55g1MgpXG3`Uh0IfACSpLB!!vMDPg1;{??50=RGKf$2qy--@Efa>|HU;bvYOdpe@Mwo7J0e9JZRe6Cz@CeU`nNH!slr`6J%-ONt<{phx>2c~_d1i)8|t%*_!kmr8manxK{UXs+1@`iAbb$ndYH<cr#>qOW@tQt7zYk!2nFtN7Kq_FplRiV6qr%j3L5(yv4$4kZFM->VjDprg9={l4^Lvk>o1)1DrHy9K^<-k!5Ra{P;eJ4<^h(sg0iJyQ(XhvLZlkLNoxNTCVY@;&SU|#rwx9c%ARJf`KZDU_6DZn@SHdC+ANs~<P@JnHhfca4-y!jJ_9UT)Kn@4=)jssvgzis?=6|>a%PLcbSwhUl1H>B?MyAnkLjCXUG4&_DQ$Gs6G+)tiS^gQ36oz2i-SJ^<VuQX=JJoIr}_>l)U+(5&5ah803@aV5!_>g#c`dUoe*J8RjEQUs0fa2zL3JAktJ%90-#2t=RUV2%f<m57=WUDy;d}ZUT^sfM|m(b^RxtIZLxC`?cU+g!qL~pa?U5>{s5MPkB`6$ezBME>w6rGrk%=M~`*XRWRITH`B<sd*tR~f%++7}L(D08m4$y+pLH&zI<v-KRqh|QPxP8av?m-em~_MI;4Ez)dkx}HrI3`De!o801#F#>inuybS2d;1;>YRFRYk=n39oC*qqt<XSEcIhHwTYn~#ZZwl!pr5g}Xd;=YrwouI9(m)wLjpWs_iPoYajkS?8a(DaTEb>?1$B!kj4)f`ytNct;@(2Db-I`+oYGg3I<~wW`d;!cI`{jQmlle{J@Yr@qR4f{Is%*9%UHUVo+F5}c_LwUX4$gjnqI$ELg|SzX!$l@l?6)9`|3E5$z6)iX(ayCSyASdjz^x?aNYDNGmi>Zl<50$U8z)K@WLrk<WAwi;SJhno=hhV?!!i<;^F!?PG$yt+8WkyX0J&#A_G_DN5iyA@6sx{ffp)#yM((k(RrAhtIR40^rZ%a{l2WPar4uh6Q)%-6~%KZ5eu>mk(-Y99w||bRdH`E7f-tSWOY4+*$!BMUp_o9d8q0f^G(Twp&E$&ez&{kzmMvwk;kZ@p%bcZ`+F=xVH;p8xLhd?bSIjmdQ%&XYGe-0EUMV~+FEv{?ndAE+4Y5%gx{oZ<l76AR-#ZWE9jv>YK=a=3y}u($vuD@_MssqxhIo075YHw-)ifLrh*8Ndj@jeba3J9J*_EQ8#<~XC42q)`(OW|J+WTDz9^JhL|a1x(|VcBOJZbM28`<cDMvI?)*7TND)8tkM)>t><eDusw8i7}<fP$)QJfUGKT7$B?kkJ@hE#&+Glz;E*pqp!UYjN@_C<lyQ6!9K^p}d{tV$)xI-Fhtd#+3{@I|5f>Cs42c2|K{6)G3uA!K4f0NK5|u8mOwdDTqGl%0b)0A&Lb!HYsf*(AS67Z(LZEl8>oIzb}{3gv(sfk};F?BtVERBM$tQV*WSXMK7|w|P@iEDHFmv>6}zoB|J~jWJ_yGBsvQ0<p+yO_-q##mvCU7ns>n8(yS~RhG_f`;4zMYc6_8GQhHMazsKycm?J2Ta}LzUblRG(8R7WfgUu_L6<dR@@6B0bB8z;y9xz11+5@y-&6EBjapeoQru1#fOzP=Q1c;gwyc!iLA%*hI)0C2NXdMUio5;z^redBZ({VT7!NA8zlwrk!uo$X#0%u{89+5{{U{m-!$@EZk!Qk2y7;m&EyXaBmf{<gLE_o*FHdyu7?yzpGH}R_VRr}5$>&HB9q~q1;O@<iD1{1u$3~t3HKk=zbLApTPl*;rd?4#pI<w?5xmgoSlrI)2b*PEQv!_^xhR0K>xDWhu($X8H4ss1Jz8dPHatR24iOyvC*9Tu|ZPNS6CDKe?q8n=EK8~5p(_yIdT-bmd3`|WFo=<jeps{>XUjv0e)=U_Pcy(dgS^8$8#qh=%@*8)sZPq4YDbfBdQf(ldzL}U$ls48Zt5NSE7lN9R%k_MYL43s|zqCrd$u$tXRaxE`07JX%IAd2}_Ju7}mH?{YU?^b1O_ENvCk_=3w?gnU<mg`k?ZJ1)k!w#We0VR{x6;~2xH`tXhvU2LDIX_vhr(LPerzdU?nKFi$MB}v@b-O=crnAk!)opD;&w(sI6+se^BEB#7%lI*^V!@m=Bppb0H*aP#4*s33IuDE;I<@a8nv>IK6Jjoum^;cBpH-Guh`(fHJAbE3#3dB1{6j!a6AJKyd2+E9gQ?V-k=kBST2b_-rz|dbs>-Ww6UjVMzIE&w{%=#Vuwf>t*z0h^c^sG<o$vyS0Pzcm1JAnE+9|sX6kl!E^d4i_@~k0nA0VkhBZ?5WGE8TT%B}#?lA0#fzp><hU;Ne-#QG$#P>*yJ1>jwf}yC*c2>6&da8{grZt*gDIZGm-RikErJn1i`Xy_5WX!Dy3*tkKkhYQeD_T#?ek4~S?v5#tyTK`QD+F&wW_8cdtr<H8+uY{SGofM-I7j15xmlr@1q1D&NXS}q*0u7_RpU{QpSR-G`J#B{nrABm6=~8DqXwI7#oB#nH(_3Ug-7A1xK)+!I>}V`z=;^(ZxOk^X@WZT9AVx?++c7oqAr+Ny(c{_F~w4Xp9kKa_mVz-^=Xglpc5MLMGeP%sOTror>p_hx~^<o%%mF&H-n5+YtZSQJu;prk-T}|=2ec*Nhw>P_opIgm68Y4_(;YD_=}2^;kq>LqE*>CFtd(nY@%G>J*2VgJ$cak)ELK&A&PhFXuF(e4RMu4R;S&<EBk&wL)YN%U;Nc`E!Je%AwSyC=7>Wz#}n>)VTYt8U2_B>G3p1~MJLiQgSZnUa#7O_cF~=1B!LYjnTv)u^2DeSEf;T|jy>UQY7@X6<4;7QC~@q?EUgX6@MwZ+bD(nRwQEzwIu8YWlzF=Fg>kCV)S5xuHIls=C<l{g)hSV3fF2JVZ>PVVSL?J~=5%X(qE{=!@e=XUG`U1)R8yrqOW)Vk01^3j1s6czl)Tqz?ONNrJt|P{vW~s}91Bj{O)Frl;AF^S?_q;gWhO>Wl}Ex}KM!MonAQ451}TYWu*Ty;iGO2B20cz>o8*j*xfz3dc|wwkbc#NTl!&|PT$bqyZm9hC%)W%HtUmW%!}>XVoi64sQMUlP6zbxzDQjMb+V=6b(SJ$aor+tEY|DmLkrZ;1I(?IMqFI!1QiAu02?Xr!BA7z?Y|7Z>kr!YuS|0OlFqsT{et1plPS9ggc#Jjzf)%2c&YeJQziW=7!~s4@(>1SKZv@-*vRtaJN%`moZQv1@9Z-QZCdz_dJ<KS!wsnwWPEdNu$uIYNO=31TgpI$s#>(1$^di~3;K3QkfEt+nYL3oO#9ZFMBM6zwl65h7Zl6ELm(eP}Tsvy~V~Q1S@{}`Es?}pkZ_Tp9L6ZDhkoO!J2`tFBO{p8y5z7`!bn>j(nN0^~OOPO9?8p~SAOHO8izKa*cPJu&|2{c8eev+cv*X7n9DRqCNy^BRW!*>_P?xz#emFUKqDKmY`6*qYfDNX{6`@bZE{zn1t8A8=7X&N^sSY#J;j<1&&6FojSIxWYe0mKJ8O(@Ii>a$lMU0Y&8vkxS8Xu(P)QXU^dlWmMLGsYJ7X@XO*fGk!=i8BI-dp&CZ<4*!I5&*d3V9kM?t61K4f4XWHDbDA9x(=IY#Afumo!sl9qw~&b$m`)nxI@WOe$ao%y>8k4*PybR*2*%)%oU7<2{NoNL@oY%9S?4z>cw|<ZPfX^-1$73N*WvB3mYA-Bp~LnTz9NVe4s^6<Brcjk?GjW>L>Ayt=i>&)lIzhzsHjD&-}kC#T{PwBF%*C75Rc6oUr`=A`hlfCK;a>Q_vW?j-_uzKdMok54g?xv@tP-ts8pp4hk=)@R<?4Br!p5-5E)@|HKzV0Dq)jE&AnVdiNuHogqHIz)yj*$CI@{6`k6&p9hpTj#oN5QT*Zv7NT>7at!4th81S=!WNXc$_bev#1(UXNbOBw+fdPUg0f4-`~sc=eOhT=5;3ik`rWOi*sigA|W<l^Md6vdR67?D)s}Xb>XrwqBg#d@wQVh;|{J%mjk-sc{tjJUed9&%#0$Gv21LpB6KDF4hup7JAvURmpc=_rW+Fm&=#?f&kafH(fc0t8Fx)FP@0@kU>Js*3*35>2Npos{&TVzG1@C!;sk>=0$r&RG<%;f;2{FLa7{wCv`{vBWK~fQBI9jm7DM!E+i~W28upw%A`S~A>XHcJD3mrw@Xa|i?0I(^!-ed(HS<Y)3?+!eaaRj@{6Rd5hTOy`F-tg`uWpy@<JJ@YZru&Nd+|K<+l1dbxbNCEQlXh?8_SvQy)>Gi2MrI82mX^|hh0U6Rc-1Yxqs%?L+zP=5t`A5Yte~#k{M7ro6cEjw`1dtabu%z{disR?#FzPD2f=3Y-jOCRz{#5IuVRpH-<Xi8`${aM#dHrd%ZM#=2X8?THD<If7p5YBZ$5v_zmkX?g4v175R^a^l7I3ccuHWQ~G&w!q(~sgGYyhukq1VF5rF0?<{kGEB)Y`UT0G>ImH+ZtLi#m!X+ZXvB7ytnrO!RBst|<1b*~y)-^|9v7m9yr;9Z;z_)5of@AZnqU@JT#k5lgFu1<D4OskDqoXAmkCFz)&8@&343eN{r;mTeRIEo^(J$XM!zE`wP*PXV`D07M;GOU2*~U6}0DZ~f9Gy8zm96uK6i$c4A0PPxY&14&OcGpaCSNAvAt<Ei`DKULx|qBy?Io9}jPB`!+HAu@FkAx`)%voRq=3DbuEDez0=v$j4S<#;;fEt)@Oq(Io-JW?4ksmR$pOQ8`J&kdO!i(UNdYtxN$Vq$D3vBEZcF3@X(h`W+}ib$9Z4_@(L=PGOxV15RhdL7VPX`;<MX`3Sc@1VPRy_unU@Yw>+<6|zK<12ddQBWj72Z<j)>AETVb)cbQHCYP)Q6k2=^k&P|e;HeZ|Zv)a!>6K>ICRWoHuE`+AjH+8;uWnN5unW952I07%orp!jiR%DYAx<t>}Ek=e9kumn^Sg}QE>HKqFaHhJ_ZxZqyb+eI7N`u-K*hMR&)#y9QdiAS*2CKy9!_x8K*hj(1W!LpTg46v}jz8h$zS&qS`lVKw{S}N6zfp;YG+J;bD$KC;x-0*c6Qc0NDO0pUg&{szyiit0%cMYH2fOd`{R0~=5DJ<P5jghaF-Kp|*z`^so6|Ru#8qMp`toI@LD7=F!2OhKND~E|hDK;ESxE<QsAlXzdCX@D@*?Rtw%-NEfSpY`-X-h+s6iWkGJ|-JRwl^YZ)G@sc+K_)Q4@Jz(8mTLZ1@>mW+r<1HBw>CL!w%22BXaEGw?MiCvRq0+;hG=F)ECO0;Iok#`%&|C5pefnzK$h>@nhDJfwAkch^i-7z}27!QR8#~VkL=pwa#Ks0<IIqgwC0j8y>PdLF#J00D6(<yg6qh`)8z{=zJsx64ngSZ4|qIC17!&N8WF*g)fjHq<t`=6$&H7%V@Vm1SXf-`g~Uc7BNqAeT4&Wl%7i!gz_?;^{K%=zJb`VzniwmlgHhLJaj0;E(UJ@1rf^#*?jwUFD#gH#E(Y@b5~bewrjRh*ta`S+-?mu((XEn-B3;JXXw?uhMYF-6EFaphEEk*#x4N3{dKMTswPh|M~8!Rt|6FH6c=6*4GX9pX$3ZtJT);bFP=CO617UUr>NN<HhHXCAm*suaAhq*W3Y<WaE6o3=bUUL7>{eWfuoCd*VA?_@rk*1jv_+{J(KNkR|C9-1%w+WI0zLS*glLJX4-2Q;Ja(KYV(qFDD9Cm54x=cLb@aarAe-dQ=^Sb1V*<-107vGXF8uJCr<qEX?b&#6R%nU;h(LinReSVZnKGP0*tsaz|hbz0*^FqNYHt9f%2qVZNSk(pIwT?0|Yu>P>=-n+<ljk)E&w+IB5<su<Xw&CHt*TOl#fD8Awiu*$N%d9KcC_F8cc8_%Gr;h0Kye=3?=CH!J=EIc^-ooE&gm(2qYJr7ig`5?o(Cr~MBnv<W`>p#;;@EMIg&TfVN$;Vdr%>5J%Pr{VGpDTJ7^JBGf$1ollUn@f9T{LC!i#B&&GydQcFuy_h%16QQd;8o(A$dv1)5bsg7Ac0?{y_bZ8{b<80vWdvaFZNB~N90vci;<8e=_@~Q3v~oYg7vlcumtRJrj2&$h%P^+#q2Rm={ZKbA&Dv7^~Qp4w<UD^7(?<rkU^`M6YRTCWB#?MpHL`hS0<YJ%4bD8UT-7%w~YK{TsB9WhtYFUkQU$bz~Zruf?+!AGBSVln#@`0K4mJ}@vgqW;#0D|M<xgWnGTP)HaCo>Mve$~g}*52PlPca-VKI9QK2M!H&Jcdww0w=gRz5I32o=_F}R!5VtmStv+?dQVzFK*@FP2xhKT3kowI%T^PR4gP%s%6K}PRNM+2uu6)NKTzISCrXo#$WCpGMO5=wvMe}ukrqY4ojXd69V*r*6ikvNxh<+%sb^=523fsM{!+d1C;u~;4DqiBG;vr4GPuKr-0)i6DT)x2FZzJ`k_5-1YX07D(1O;T+K_Ja|Fa`428v<<HKKD&%N%&T{zPPChmN6~4Km23+i`#s`pM4X9nF5lo(E?Cr0#HWcDX<(Bxz3fgQofoAbh%0kK@n75+e;A=>zFz3qFl50FJW|D(tZ@1A0$z^DwZQGJL}@|JDjBg|1Z(d_MUc%xMpu;RMJJyRti^LYHmg_Ni${jY8uZxl8&Sw29RmHsM~a5};p0cIRzn=umRPP_gpqLaw!+&9(~@|F_pL>3P4$jVl+VPhy&uODnko&#YQzR#qIkRkj=q{(D`Bjx)(Y9|Dr>C(XqT<<McT4HDvr+rLk(r^bz1jmmMs_MEwLTdb<@IVulYF#1EzPvrn=&Fx2c8pS0{AQ5q_|?NUml4!_2uvsI^HAkk;yoG0IEd?@}f#3Q*ic%f)UZIb|;H0jpQE;+TmEh2{N&paRC(UF1c^_hcMMk)=8|Q|p%Al(Q_pK#{XA0syBnNQ`^%n<EKpPLW%S9Z=EVuG5MzmBQfa4KXTYKl&1F3z|YX<{P;Q+N_k52hI&=D<}s8Nj?L<n#W5PRZ^IwlqOEwa|3z2QR^28URjttuHWkL5;}91vr^cL8`xp)q^)<fT+){g@weyUZ}7EI`4u|?Zl1+xnBY+R>_*WF<nmfJFK(%USc)K_)cc4Y^dP4FEMgi{t(l0I1Pjt@u1D00uh3H(>Wggk3U(Hjpt(_ek_`>I@y`@@G6p8B?yp|AF{PA5$L~h+-1&(}ymRl|Sg|0mK@0zeYKa`{E4g-b6WlqSlR8j%;RMocEh1#SkKBPqeaDuXvaPjcvePD&Sp-8Ox-$;}w$-7<&gxy1X<qk6T-8hNrbY{;%u#jPt}3;rVa8CyirlU;cYzwwgPrAO*`h}C!%%zTVq!$BW`ep5Wo|#F$3DkEN&et&6rFaPK*l6FqK1Boho?Zw@RZF_43;<5t>77f@I<)gskw7seK`wvZi@M8UM<O>`RNd)+yqX8t=fwW%CQsW$A#@xj3g=+L><0r<dNOa+kMT^99{)JN|LAZWSL_2<+;^VS~&6nYgQ5?w=Z+F>`B&3QWc`H{yWUbr3Zv^7L$3^f-A~ofpO(ALnzJ9e-)FNGX+^CGj_Zv66XDUQ0l3n;uuSeWb;0Hh}YL;l_^mMMb?FJW`hkkPUCxT%=Sh6(b)&H>5-IpggECe(u_l+GhNL;iCEPM6urg8r#3gt>KGClJ@Rqa=Lo&XDeCWHhiUCRrC=)>?)+#yXO~>F*vL{zjv1d*>M>!XkU4B|G$xtgkmC=)owKu$FKz@o)sCrf#u4`s|B|(4lh#yc6shI}7;f<hX}~iRb}NkK79=8RA=V}xdF=SKqPTq}?4KC_v`-AZ@a{`PyXjNUarr=)-cX7Nnz4QNS4)(*?0NcsI-Xv|iRFB0jg|%Bq@roAqetx%1}FC{AWFV`uK}`KsUP2JEjR7@wNZy`m&j_88xOe|a*S{CPhlVu-{~ak&_bg|3-D$%l487Gpq^_a&SK&GR*voMC_qy`-ws<0T05ZamP@D@c3P^PjK0HgM%$Zy$F#1}a2nvnc-FWDwGV6?rE$=%=N-<V_vjw!=*LVfW4r_9X~3LMAr(yL@F<%p^RD4`F@~u(j3yj)5AkgS!xd}}Ebcrm;TaYft4UxHi?!st5M3kw=ydixS}oTh<lkXHqQ;+l08Ca3*O=aVt2*1;nnNR&FWCwb936{Sm5k|Q-EHbeUaJ_@d$cJoxf5zTK$cy@Zb!mu2cfiMA<Rd1d;Oa6DUZxHHBwHRe_qM3=FM+NsVlt$y;LMayt+LTt?(G)@CG}+zyt2J=^^d_535ThVwkeC?dcwq(S>iKT?L(OJkt45|6tsFx%zn8ZIcve4Yj|+ttWF6?)d8O%>oN)uRyh%wks5Mcm@WxwO>@UC{-L)yak~%GPJafYv{*Ou2Yb&EkJZl<~p*k-)=+Oi~#O5s3;&GJ@q)FcFAJ6npL)Jr{LoH{^jCq!OmB2!^0{E#1zAb;BMR|V%)aqO>M#p(-ivmpf@r_r6YGB@>IM4ZWDA~4__kPEku5l=A}{M*N}ujTUJFxeI`|JbKJ?6xZ!sZ7HaE~!1iKewr5|LA<R*FN&g^-ap&}8EMZb*{?ZMv3;{5_S9Ibqv@CP-<$3FYB0*jC+fg&u6(%C<Hi+LHdzZ0VYq=0k1+D*TkAL3?d${GjqOsnF@c(YqCe3Z=-vJsqgGOl6I^D2MWH9lhZrxVjY`p}*NMnJj8m?AjeWtHgFIeaX1zjY%wK=qm*<?3E=Z*`Me7`vX?I(0iEZ$Y7O_2Hl5XqdWgBFkXh)`m?<m9O9HU)#ci>-wqtU9B&tC)LIatt_;0(O=4DeHvJn?(tmnKoBC-|3(s8L-=hHW1@2BgKugXTH(_*HkzIy<4TriA<o|K?ZlSEEoCI+yK?iR<_CjcoZ58cRY}etrmB?UA|_Tw#wPd*B3Pt!;fV)Zpw7bEe2-X{D)H}&2&}2UN&S^(U=OWT9FLKT=Sy1_woM%YA}vM')))

for _name, _source in _LIZS_MODULES.items():
    _lizs_load(_name, _source)

from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig
from v23.state_encoder import get as _lizs_get

_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-rk<U2j`ia{McXpXWg&MOx0A#^#QVwMT|5FR>X2g8_Df0Kw*AlD8oLJ(eZ%epPo>^*NL$z&@FlsC&=%>8`G>{^fsO{@ZWA|Ksn!zx<aMzr6f({rU6D`yXDs{P*Af^Kbw4@S}(S{NuOZ|Ksof{qVnEUjF#yufKk}y?OiP&E3ndzdF3zUq5_UUwr-IFE2muKYSSfc(wiZ<A*=`yx+f_{ObPxe}8x}dHc^dw|DRI*S~vzyMOuZnd+y9cVGYf{^RwxhP}BtJhT@4=JUJ#{?oVLE!y?@=F7ZYUx(`bn?HZ~bbRKw2OjpH?;by$dNTPq`;%$k7H=KC{n)hG`$x}Z@BQ)1`wwq_{W`aIUmiw9e(&Q{&E7kEnAGnN*KhV}x4|NqKjG<_Ki^Fn84SsrYoX7_uSWxXeYd|&-m#b}v}=wV;N$+o&ChtDEygxz&vBcMhT-w4@z3Uys<aSn(bGi0H3{E*YU^ke#~;6qBAK5*J+y50ve7d}??6j2UH@{|9~aWB4Z{*hr)2cK*#H(-3R<x8=%X(_j&OZd%pPb=)ach}ugbT_={e(fpN?)gL!+}})E=-P^+tesL5l><#-cUKY;4@wAgcsT%luDzP7quiWP%?5q}Yn3iF4)|T5D~{=SAAb>|#efhr@sRw7dh)JnH!xcxsN)26xm)Z&61b-lRQ7eev4DEAr>gKed>Ix{0pYdYLs@FylbmgCCYHkx@I3zZRc{Y>MF#$KR?CyZP{8|K{%3KkaYt-hX)iugk-Bcp(0+y5OKg6g~1}@yve_?B=5nIr{p;k#h9dfb$9N!2R`dC5&u=g%vNlxtT>A4?7!yxEXLP)T8aR$C1kxpXOq>(>E@My6FfTJ?_j6hX+HCE)1vI<I+4=2Sx`_hr1&@Cids-!|2@WdjIv9$8+7yXjS~PX_`f2S}#AmxJ(V0<N{JaM-99nkQuof6Dv1|DH@C`ZeEbrNJb1c3FmN;;+shG06pLND+)#&MZKgJ^C6$_(#nuStGP@2^AU$oYT0b=f-^b;j+<Y%pK%9HPkwiO`<E7EDxZsC_0&CGc~(wcX~z|u2^(X9D!3py7JW7g@)G7(Rc2A9iv-?jmtlZx<%I1PkuZ9|mX{a~4ndU0v^dC<VesW?L8<eaj}B_OWO?P=?)gzA+Zx++jQF~dJ@q3q#8!RGz8<DW_jed}U!OPXHemdz5>P}BYp^BI+z>-{dNZac`QQQ=M>U_zCDft>L+VFtXcnL;uxy~Uh6+wXvr*5Mga+r<BGK#7$8_`y>kT^v!H~o2tmD#xHYPF38tiFxSoND6z6K2;hCo|Q!3}5P;P;c0E3ghXiFMdC`=gd+>$5OM;VXwv3v4kmTtXa3+IVkoZ$8amT{fABZ900xl9Oh>iq9kBb-^%w{$|O9QcYX+rF9#3$v<ngdbi&lgRI%UU2M?jvOMcBD%^9!;Zet~&`e~J$tHVq9zi}2CdR0!WfT%Vcwt5q1{|6qRYS9M9S$=S84$UVc^;D=nP6w23SirW1&y5mWA5KUTcj5xk8!Tkb&)PD*txF$-LUSa(~b!WYz?X=658C+x`LF==CFSbf5Uf*@Se(CAP;srQ;Q3^J<FkP^xWoI%3nDc)vomg{i$s;xJhyKE|iq2+pyepU93!P(iZmaS|MXZ@Ybmf_kv};4hePhtdKTlVMurj`W}5>Yk>?W_r;LW;PtZJW2U2iAH#`(W_owCcQ^sjAT?m31++pV+mD8WEXMf68(Siu?{2RTKkjdD|LQnV{LNiD3$Z00dUmO#2pS)ai{SvFP7GIG7L%ybMs*&-$YG*>(PUNFrkK-D=dCh30j-vfPC=eiFkU%L=2;$0Y2&BF>)bqJkE^>2V<Z5v%RJq%mtE+<4MY(kO*%LLoV@AA7<*&{5tAiJ%+QB^v|55asN{q!TRdFzT2e`20}roAfIw)#MwfbXOe?Vf8yTf&`y<;24hs4;@BhfbxVd@wcPIKYr%=c7&%)-6^H~E^X92>HMy3wsKmho9V7*162S451eBMvKIeH9(ZqR6qCMoJ6H}X()ZrDPPZEi>os`P8|`Y>DxO{1K+Rmp5pZR*ER@SB^Xu?X9YfD{lz#$d_%O!w^w(+NSyl=A3gky%`sAYJsajidFE@qnj41cN=ExPn0ePezf1H5v0@yM+mN^KoRJAZk3k!WQ{UqEUwQ3#3-SJ<Z}~ie!P7s2FsJ@I3edj2FTD%rzXUXy>f&U3Z)r)*koF6SqO9ew-eec_Fy5<y<L<R<NUmN4moa-B?E<U!>ur5>{Ql%g5F=cafLq@$0E7)uT1F_N6HZJkUzr%NGRW&B4pw+}}NJMt%NS_`Nv)Ez=rp^UP(pIX~-ja(>FLdh8ef@ZwdhVK((Y_)(Ngvb7NC0qqSrt;A;32sPGqi-Ya?2o~ZUC=f9|j`qx0a6D)Y&W&vOkpcxUv4lS(4l_f%(VPlVkp?#xS=$*tk-M?u>#Rb$Fd7y)k0f-e&jkxn4XYB}h1ms&##A_P$bbzUU(!KGZfwTEwQvFPI-|QA?ldva-;1$8Y=U#*PpwKvQ8KOBjgMOZv-?oKM`n8#d?$4X$yPnyAUKIPQ8eigLSzF@y_x0Vf12@@Y%$`e;TDc|xEK3gwVKbkJxNZ#0E@Kj<Xo>!ig^>w)Rwed4?ti^P=>0UKbyfYz@N(GUpoN`o(ynWdguoc7!>}HS`{u-0mX}TXB6C&iNKjNS2d?pT~gnN6L==i6duh?TYE-0q*2{YY_KV6KrUVQ`(f*4uznj`iG~R#-GGCRMzqkV!PdhK83o&qhQY`8AO3uby(%=aG}-a#X{&V>fZL@?@rAG>ig}|@HVj4pN%+Kh8$AN6JIfI~O0ngx2ai~wDDbG8i?g5}bHPRh+L9#qg`lqj8=zwTkQh4LSabef&mi?igYJ+!Pr~R+wRswBX(t6jCI=i!go#L4gdb9^<@#7mThuRj9&xF7*7O|2jBX?5rROytoaJjItttKwqy2RPT}KT>d`V>p7pQT44D+mbLX{2&P$%@K6c9y6(Mo%T^O~ecVFa`Ho<iAL(b9;h!^1ZoXRkle20BDKO*%}o6V{k!Q!_d=+1}dkJ4t;K6+t*q@aUBiFB}ef6zR=w_`dB?>V8C4tJ@Np+KxYB8dOQKWPSffj7*nRD>R09nukZG7YNkl0i`3qw!}k~Wt%vXA;ji&ee+J9fRhCXjckO9prcD80CLfwK$wAhxD7F4Y_E11|J>9@ZXx&25n5cZVb!KVR(9kW3?}A$n?IYQ8>*YJ7`sK9Hy|DR)PWGfJO$#C>T&a>{q(3Sk*Gw}6CIqhvR(;a0VWD@MvE>nSzEJlKFF$J*z?K|J~yVV>Kd6D2?(Q6mNJs#hWl|V-oF2-)|+n2dY)w>D7YAMi_Hiw@i0c02iE^VPLgC*z!8itC}QL|Sq4o~uz6&ilC_nC4GpN1q8FTU9ZC%{w!MJ+yQKdhDb=B;<hsYXm6O%QOGD-cVSpfxn(7eWOxYHhS}(bgC@niZKQtj0ko7MYK5P@jprC^bY5l?T)H@L3^G{@JQtO77E7vo3H}y^y<nSppv6Tvgm(+-Xg|L18F2iH5E`FIad!2^mfM!ArJx*H3+K7=514;j)cVd*Rqv{qkYa$5owfOtdtpsJCJepFTtRDsliGKOQ9@bzB*FusTPvt`)CxgJgXjab9;3#JhYL&B!s>c%3yEyrWV7t>NL_7PEUO(HUFzWanVMZ|O5F5+j&*;-|37UY#LHO~fD&LoJZqC-cyCT;N^$MOJe2nx<O>pvQ)v4pVS8JP$g@qP^Ua|ZVA|GQU%3J$qE#HhfZxjoZFgt(-F%at#EgU``B1c^b+{K6X9FdYChlp1>8dgut_QHWDs6f@cUwrAOSs{>QEWjObBIMn^b2KB!>fl#)nlp~!EVS(5i!3JJg*@N$Sw?8?ocz2IGntH?PCGhdOm85CYLi(2BdRr%(-{UK9-hGSLHHgY2!>EC`v2P5>bb}pFo8xxp(dPUE)g^eqX!2vQVdhvv}V6S{}hG$LzM<pw*WX%`FOV#z#_%P09QDuG?N}#G=m>~%JI&b3EM*iWPAn-LgoSviG&04bWJx?Pi<)a$z_3<n(pA5)S@TTLwo<zPp1feBY;ZMZ!rj-l4jZ}fU07M3R%lmIira(FigA8%9M4JNo`{fw1_)Tj%sM+XnL%hJkw9f3QoCl9TnkO>Ih*s2`7FPruDV^oPNh*m||b#Q=%ezCK6soqU-2-KxGRieluN$20k}VdF-}H9l>TMgAt1nlRPR*%F$b~q`I%1gu^M065Yj2N3s*a0GAJXcNi!NgqV!8RJp`EXSTtBmXM0YX=_B0PATnBpIgKJhJcBe@khj<FvJK)N}@>-h=<neMdz-P5wy5cnu&btl0;^tz)N=;$qyIq9(RYj;;xj<YVE*0Zrz%gXl<M*Tqm=#<O4^OGVP>5#1|_H1vMS8q=I}3<rtDM-BxTaf}x7EbSx{TsLhhY)Xns5*4sHKg-yc?1|5?a7L!ZIEBmT}SE@3fm37yrJUxCPa@bhuk*pKXCe}oj5v!bLpF9nmRY%83+Vh>xoGLAIwfo+@%!sijFxdpMBK|f@()VM#q@E5d>0nnZhQ|W3r6XP%lisq22t`Ub*aO3V)|bhh7soG08E>YyWhBipu}5;9g_(3rLkQ~ffYpkAn`a-WdjmRlG}{^R`3`+c-Z_g>F!|vvKev#$y`m1Qusq3G6crI<ixOS`0zY6UoS7_CEV4l4yB<KX^%GXQ<_%xEEnuCO&J|?ZP|)2;Vdg5tEoM3I07O%W(~+o!7JNO(tVRbLY^pwz+K4$zmXOtroaVEx)*va}Al8tgKRtWH;|pH#8J5l2J>@z#a#i^q!_(A^9jVTE)N07l7mL@ww!tV47s3E3hZV}Dt~qffa#Dr$oXAlX$UIQp4wm*k{R|6-%}GgxlU+}%^f*T6a_(PE_(2n<=UM%Hs9}caAlW_)5yXf?BJSVI2I3P*6U7m=q~Vt$ZKba`lgyn7X*>+sUEm!RM~!8B@Eo|9)X@g7klZ=US=J?}3MzECQZcYOaTXo72gO*USRWJaVC8~3;Dk%qeQaWprP)KMf`K#GF+q09Kw3geS)&<sm9Bw=DF+(iR*|$pDI*b*jGZWTP2f$t3Tt$5Qq!U);3lsOeyz~0$0A~}NndQUPEKKERh$LfR_jEs`eKZ%?n$>vRMQkDCT}o51Pi;1L`1C!-uznWTTsNSMJxWN3|o=NEUrV=fXos}vnJGqPx8L99<)dpA*vEx1{#iYrQpaODSm|5r8Yk9E>Y!rSaj1Y>7>^H>p=?WP>6UVAq0<ELaWtt#{JQbfX9C(=dc#Sg3({m^yaCte+iRe(?YE*??{&m2o^sXFQ(IG>-<mG%bExJHj-H&6sS57ZYJV-P#?%FWpU8uhlHz}IBMY#3pRJoQw=4DLf=#JzN~gZuOK=Gu}E>4FiMCMxd2X6soRkxwWzaj;)z%T;z(;2du<7Nkt9Wkkwx&Fh7CGZaZqd(*K0?`XLycM<{#%~mP%~&@{#7fJkP%6iO_VrTe-n~41Yy=EsJ!4g;j}D;)zoj^{IRSMBvNN87qBvs1RA=yc~hwkG2!FC{CkUiB%q2FnJ3dBkTjyKW*a+DMly}uZ4C53xyTqo)kPyRs&hN@av^A<wj<JLqW8P%e5uakXRPWB{1rtxu?1Spbd*qlJ^u3&C%kB=n45TjZ4zoV41Won{yYu9EHMxiLGM}Urci6u`m9e>RRX2<(LE=dpo(3@)MB5RirO_h-Tw!ipzNby=Og`zZj}&WgJJDk(1O(tqxV=L@6y>FTyKQ>KTuvTz~*p;iYm6$de>|c0+=rW4T@AQ&_Tef)OYZn%4KGh_T>&xQbVlc7w0tqR~q5WK)=%B<064bbU>3%*smDK4&JYRNJn}3__cl8H3R7wo+_b95XD{I2ksSvC<_U&Ee4c2`UVKXOxE6Qwmw=>82{vkk*<lLL|3HG6kMw0?>`d#h)Jw5`aE5%h9A%kUG0Q2U3L##KJgQ@(kfgBkQY$Yp9%ah{DE}SlX#1+-z6MI)c(@%FG!(^+bqfwB#{3igmN0qufh|2vRKgx!5YRjzJ<anXxu{8YN!Vu%V(>LdRGQIsX+tjt~>fkyJ`kn5qNqddSn)Xe^W9#G+<ku4pb{zp%M9PyQJ>EnF71J)=T>!t&=zS%f&*1j8y9fEP0R;WX0Cb$Dw+#Ee9mm%<jRuaBHR6(Oo3Q^b{}ca(<93CYN1zAe@5r|cg=*k25jRB$SfjmQWNOzB0s=*(FOj&`D(L~3S0h6FBL!EdlaH8wA+gd%UumjaWl3dsaQ7sK#JbXKdhg`@kCM~f8a6~QJ<FZ5twZb9~znHtxY)<i<oaC$h~NX_-Gc;!M=j;BJ>l*Ez}%<8_(gV)JJBELf~q}<>y(9nLg*qw6?E>X?Dr`K8#CMR2)*<OPWbUGg=PRpebRRVt?6P2&-O=U7kPa{cLo2*FkhjZbuT~F<XFnV9*yv2L9NHxie>FC0sL@$y(NbHua4M3n9ydQR&zm4;RbM-jz9{J=B*e+=w_Gz-6T%R?xO-Y=g-d!SlL-Sf$c*QbV+u%7^#-570KwxL`<r64Pt_Rg}P84GEqZyXewdqs|KD=)yT9wf6GHl+JmUWOZx3j6qbkdI{&=1Nq1FR`6$!x2^KRXVfCH4){uc<59s4}{1$?9W4$vX9u2w0=zK$N%H#&}J=xg<0f*xcm1h-)NQacmV9B_ar7ot(3~#_T$-ayYC=atm6AN^6NJ|8Y=|$jdZ|Yrts;AO({DFB7^mAhV+@#geVi`4b>o65ea^;WmZR)1+YI(k}(es;CUBm}DfbrxutGPFHg`+y0ln2BV{woTe;lLIh_?Q9)^^#D|ZYlx5WdbhR#m0mh*kqx5t`RfkrtE0Lnp@dv6g5}ajhvo@7Bi!Gb*CXanLL>ZTh$h4J|BH#y83qWxyMg%X!)TkUUlU1ozF)Exl8f?Z2CL!-2s3FIC)*p4si^#KsUS&JLc(tp91E=7d=SmZx47eiaoKm?c%#pfitQE&^CR80aul_8k@GBH4h&=@&hz#r-{ZL@Bo&IbT?U9PL6V4RDnqEIA)`YevL`o23gT=6&yfC*=b{<j7<c(4y*ZjvvgS->HE6-D6gaf5`4O5lcv@*JIY5L>&e|Pio`tD{J$kt`YEW4b+9)V7xgHgE0S$ZM#21twny5wi5?#21xmcS;QB`H<ybX`BKCj7(m6H1s9ENkYT$BmXMMn!s32LWf}EVKEUQ`j-gcC!3u!bcEH`z~vbY1(pPg0Qq;3O%dA*Da+$(NQ7wg*o&P@Z|CY%kJqaj4?wnT+g+1(nGtfRg$2?B4H4AQ_lNHXRy}-&GXVI>KUi*2O>Kp9#=jynVjuj0<kJ*O@NODliOu6)&-@>CMD7F!LKt6wA?L+!Yz-!$0hPHE?e`32{nuWMtT7$;qGOJaS;7)Nggz;e*`{;S?qn+cMR?Y@VyhLQRFOO<V6!c>W>IAH8Ck2F;_4od=K)Pylzz!F<dQn=E!59#FZt4nWWdU{>qRexwL%A|BN6R<?$rt$(paBiE~TC#^h+W(&a}{Y`~x}JK7;hR-;x|Ie%t<mJa4031U^s#HkFl2-%}i&pbnFva_#Zs@@fXR1>>qnV8s=YK*LDQG-pF><sj*6T)(c4sRMbj3_x5VDLn!TA=<!OUfx%5HxX@{qj{s1I~$4S)(A8=}~B9%W?`$nsJ2rNhLpWm3)^o<0xzEwW<|AlWXdczH|y$6L}g%Pc7>`{6?GfF(EJt;0H8AY_5<~bFN;2NNS7cJ>^k1oGUI6SNqiRh$1hs(wSvo=fMU+IBZ%~MpZ?3YP-g{iFsO_a_Yo~6ra&f^)m5KooerhFNW7j+0hO1=oD=ya!pA489_U_zObziz89<B=7)t#zY(^Y8*R%$K+jE+PY0dd2j^kF#rIqQjh9*?ldJ3yjpH{tkN`ZhE{F<}BF*ttaL{Rf>x!nUUW*c16&Qyn$4J|x1n~|*;MAqxN8fMDg(W8!TIM9PoK$gSxa4HL>C?nPshDE#z^ZdHUkE)J>J3--X7;Z_`6j_DQaKD(fzoG#l~#abS5EBZrI#$onnFu{4TfjJ3L%Ar^D%ck#W#X^)QSgd>*r3`2v&N4@Z+Xe5r{}Z&>(2y_)Dlv2+^AiSi5XvY;x}Ex}J<4<YY;zMND0kQknJy`CU7S!#l0RLMm9mT2i8nFfFF6%p7`Sp>8mbozrw4iq6GZrOovJ_y!fQ8H*(-d?ibAEKA3Wj5SIiVA(bjO;>_t-Fh#awi_FN!$x8WkO!R=Zl`x4FjBGdBy29gsyO!!nv@0V8PBgHM;BE=1dQqBB5n>(B)FlorY)%>0se`h*P;d)<Jj1An|$>J6dXMdy{GR>Xz`R!1c3)COKe9kh;mK5Jo6H3(s9ny=j^?wtBb|lRY^EbRNE+oJ3}wUSE3+kJZ8kqOVQUDp#^?8-Yx?0HHnsKHGV@VH;HmrRw%5*u9Idt@FZ1?FnBpFC!@lH#HSm|`OTD1Q=M-@;uZB$Z3zjjkh68%u!+X8$&%O}r4C4TIn3e?f*xSt7F)HaN=9b5s`Sdp5J_kiM0%`o-n<I49Z*%_+Y8^x&S&3B04gHG&1izV`|pzB&WoRNNj;HxSQAuyf&^Ab`+2p)IqcK#CP3>Xz1<<Q8l|a7<S4CX>SscVB}BIr6y2q$@ku`n3c8w6KbF*u^t4%FdL>fO>_a140G_2h9PiDttDvYPt2Rie>9|s|Et+vLSC}lA2~t;bd3!X$VNtRbu}K(Pjl||VmPLTIs8Q<_l}pb4A<VCK3YSnJnpM#dBe$e04j-;AXJ3W*Xp@LyU5QkLQko?v0P=yt1CN-%ebiL-3^BvH_vpN88IX>3I>{LkMXgX)4m6eq+4?YKK#95{)Ud9UT#Q0V^zMS@QchWle_No5=?NlqHRj-gt%3-v4hd;^VM)Bgt;8UYj%NhgOZ9p~1cjvKVcH0LR>f>j-ho!7%_?0e)y`Y+9iFGWlQu}6VnoO2)N?1<*{mz07Z1*>a`SCGCN`cr*1a5ZsUT+FNbVdG!1Xzd-oW7Cl;Ql2qEQ0|ZAdm^P~%2AHU-!+h#^8B&PWt`ecw$_bGn7M&&lH~74+3ffEy{}(;*MST<%OyGtKi}Z7rszFMY=qE*0r&t8{fCj0`%Q4auetM;P1BNH*fISCfljzBp)n&Y7PO-GrjWh`(obnrJoGQmX3!7#BY?omP0*a(<)8rb_K_M?{Ix#PEo_f@$7mZpm4BHFJavp-u%KBpYf{^5inT-Se!Wg3{O1TUP~^wZhaRuBgrEC~#tQl>=d~GSIui<|IG?+K;5V3Mn_BpEynKhr63C6<Nx3@+PHY;yZP3>yZTkr6c(P%(nNn{&MCRC$R_FO$l>J^4zKvCBmvBx{O(~G0%x9K5}-F(KnJYsO!ke)dis;q+q?!gyvp7PjhK6FSxiSx>BPlb1|QpLs8l-pPq$-unp0+jqeVzEHg1~c>=B^`T&_ld$v%ZfmG2^DRb~>U=!9+E*wh=fpic?<%|@H&8f%}x1I8UPT~g%zmnR|-uBw~r-hW5<f@xAXhqulOD_041r0X|9`*`x^ET%~6t$wzO7$GCLd<21h|#KHr?*!Vx6Sb&cos=wV!__7Sl`-4_(;MzmVcyNJn{fj@NsSFWA5xRK-Yp95GG0Gdg<_#R(XyR)p_h5+Rre%g?=>BFsz*AyaFPhumC<a)jdhE4x{s{4lEf<2r}T{k-}K;QARv?UCH0zwhx~`J~oxg=QXHxXf1XG(B?dS)8iFGYrat<DlNxM5-I8Yd6*R3fMwOFgK>Z&8UkNfR(fJD5n7T>OL&sOm1xu}4atf6%)m2ZG?<9An1?1MMT)FGR`Ik8GzqiiPq|K)N!_-b_riY7#lCvn<+R2-+H45BfQwS#^wY_0zp`^Az$nxO%XUygy$pkQ(|2R(pMGs$C67H<+>@+GdKH_5e^!z(KBwAL5+tO=l<uLYzQYoyQbnq<Xz;xWt&U)tdqD`ZIkES2!ks=uyW3b~=MbY+2hf2zsWb|cWy%Y1HzMZ(dC@OM)TL@o5tCeRo|DLE7W@>GqN9T=rtc+~S4L}`1eA24$=8VLc!jBsyEdvLWQy|qbd`{2YJ#p|LQ?p(8Gd3F#}TTlUvwtm2DQW~y9m|d3F|fyeWr?nYx>J={>wHMs&FAHs?5+CkU(0JJMETiCk`AV=KIQ~!R^oV7j?<V0;&uuBg9Le=k7IVWMbNwkS)-J{ur`uM68#qF~-MBTbb&b_Yk*c@!w^veY{$hu4}yc3AwTrXyE8^To(p=wD~8xl;hVKncg|zKqL<iMpAxL++LyP_GCqJ|I4bM5?65%<SMy7W31vYF%?+m5KbhvikU;%SjwO#ddrP&nwoPPk%NL8H`5f$|J$@;ojNI!Dl5vnaJMbtL|6y**H+x#1Sj_C6npxT#6hIRJoq*ZKtNHB-Ont|#(*DL^URE^x`-q(SHe3=TJa0fuyR#;TC6={T*|CPo(oSGxsbVH@SJ-Eb>Lc%%{ng;_X#pd)Z~^yl+jjbk0IgvCxqgNI1gL~LaGBSIK$nsJ|mMGf>Cn7{M0Sij76tzzQkAw`4$I<hv<VsPcX(G9TziMi2PH*Ep-s}LsBKI76yT<1OKo?_lsoWt{*$}qor!pEL&bJu%0E^KQonhopURAA$knv69Ix(Rgit%cRUd6$Wi%BtWtY|K{6Hq^p!glC|fijV3I@>8WlX`9OOC_Ue9hv%mJ2{rpWK*MPW?}fgsfwTq^?`*y3K|ndA_6v*3MdO|?cUEdkM9a9QG$H07R0X&V*^p6*ya<!-GqlIVawjmYghBM;J{Q?`Nc7l#GTPm6V32+{}{W6>@@4vQI>Lx&#^NU6IMkx}Y>1RT4u4Qr*TimDSfJXkoZXl4ejW|3n;A*kpF9#_`c%qU>_Mkit<%yW&MdO;VuZ5B}|3F)@NBUCgpoM=P88M7<d1FUPZWvM@h{;B|V*U~?nh%jE7oRi4{(0xT}2sRM(4Sp9bV_yxN=S$e@)d-uBGY0mX%8%&^DLTGtqb&;cd9PB08P?)WZ?CwSqW(fW6l5uusyFG;FUWANos%e+CQJLv_uB|gn8FnOqF<aEw#e_$&LWpy=4s#v!?7^~WZregAlnMeOO7@Z>0cU(|KIRo+M}&#3TkxjiwWZS1RuXnAma78xZWw=EvWVD`n8vY?X6A38YysGH6z6?NA{pXq6Y;?Pe-gPI=t&V4oG1ZQFR17oLtN)Htdpv+3Y$L6sYLcA)YN>OIr=lXMAT@TG1^I&qMNovW!+vMyeIdss2O-Gojk_tWu5=DiI}j&QUiwtXwg*4N5R-kyrIP>r^;l8HX}QD%i_%Z6o)^ttdzt>W95R6sx&tP~Db*v(O1Z2nGBid}D7PElN-zr8=AxWCQR!*8;?M97q`9E*B|!6~dKmcsfy$4N3?)i6Q~34>_s&4c=Bl7y>xfiN{^?tazliELF@-59p9udmJmMpRdwM$sqKAw9jNA7%as5O*3Pv=L|A71#FH-sfjs`Hz!p`s2G<zJm*ykU=VAZXk-*-%r+ypN~!-(%d_rD{a2FAWJ$AW>T_fQC`N98k*vyd+w@UY6aimLD+TNI>Y?(>zQ&<QP(++KpWhy;RtR|vJg$T1JSKVE-F&>hyBTuYiDuFG>zx!YsP22>iaC0`6Jv4N`BIN9BJO#FF-*=RMD>`WXaWH0_+eVZij*&S;^1B+;PVyYCu7pC%Gt#)a_ev}$6+f{ZkwsTR0r9m?OwP`&?(<7CzC~th5YYD!4X}mWK#;rVEJIh;D^vXkpIkSiiz9MoL$P*S8=NT@@FCP1mHtnG)kaTxiw=ESmfv<o3-j)PUV?J4g?oMsCF~Xqg<5J^UMA~PlUKqPfhR&;yP83nWPA3U#VUpNzJ1vhH`ydlJA9+*W9{Pi=*_yQTF3-m0rE$kQYYG6N&}TrRS*xsnqC(jkM{(SA{@?q5`-~M1!{3wtH$tLnYxsG|@cd`t53PKmpa-U^=5oLQG$VI8;jf<v1!7pN)BX(Dl{RP!C05p{vjW1)}O6a)`bKmWHuWd*sdw;U<<PPnioWa8%fS2cL570Upa+h)RFRq}9pa1Yvx5ry-vzDx!d{8F7P2Rt=~h&w~<>G;LTwynd}#vjMe!NOtU@{p_r}y@CVoI1;vtGst&<_~wBr@Z2OM`1sPpv3O&i=Pa^{?q6CPh>1u8?wZ5Oj>`{JBED8++7&pa@cm+~UWIFzb2SHC_c8zpDcbw^B9m78tRl%WK@=`{*j@FzTP2)u)NYyryQ4@hU?69e?^fXW*}>^upKVZ=lIv)|0$DM+$k%jA7NA}<;Dg1wlT9~OBmkm!K)uGuASGde;~>1guM;q-C;a1=_aEN=`sU_%YisqZI7Hb@#?0r%;ddR1q*~7Dk-;lqC^3Tv+TpoBE2Kj%URCjN1?362P9Qi>u=_v-MO$T7zBl6qc|qEM`<7wlm8r<9IhkUuaLHMvBi!YsAY2@=X7WEQ<By~VaAbM{?_V{nwv1f6s7L(x)=>sr5>ung4P2rdjqc*=xEw@37GA=g)*T@wc?6=KvgX>7qpTyAt{VlJyo!ld8OWBqQdnY2E;8Cj7A;rHGs*djF}-x6OS@Vp07#y#%j>;#T4f}=hvoL?;02<yscQ)OFk~nx(i$Ky@Ubw`v@aJbqpJtiJse_-7Z-L14tv+WF2%!k_bq1|KG04BFeCR|T*SAn!D%jP25M`RmLWqEeWZ^)bucOMml->Ss?3iszVuVi0!8jg&h2<cb4}6d-^XJBjHfw2w8ovB0X$Pi^ecq&yb7Yj6+!b;|3=U|${_-uhQA0N$wk|87!uIU0QI4vMB7OPb@!aW<3Scn*}E35db|u)`i2)-d$K7u4LSM=r;-jA6A7YXh`Q1%b6mkqBCXw5_97t0kz+_5l&q-6vRpLSOGslp6%5=($bzpS20}FEP@}y;b0g)ZG(&2UV{;HmH)imj?g^WnWmFXrNIVMt$G|sE2B{sKRYy-SGszeIDdGD<T4K)9=k?!>SxM-Q(3-Sd0%}&n2MpFx%f#rusHL$+v%l5*rz29<75<aJg;oTEuY9$nwfd=LBfz=Hqkf5%F#X}M*oRM&SwbuMAj-^=2>SF=kJK$Nc5^P*l+8Wt_sBoYyFCB)!dBk~!TLg4DH#r?h=jbsT=PatC4F50Iv6VeAHJkB1U@*FVMOYd<dn3wW^24Wp4NhPyK-bNqfRH-DaRMOCaS`{wR)XoL(aTo(M8RhpC%q_;{&lNTOe_G*D4_c(IJ?}F`rtF)rQFVfghED(@Nc-+VC9Pu!e)P(e5G@M<Xk~bJxbwiy(Z<7sIIB-u?dpW>b?U')))

_PLANNER = build_sparse_planner(_ACTIONS, PlannerConfig())
CLEARANCE_STEP = 630


def agent(obs, configuration=None):
    try:
        # Step normalization: Seat 1 in Kaggle Environments lacks 'step' attribute
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]

        # Base planner with closed-loop weed repair
        action = _PLANNER(obs, configuration)
        
        # Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # Step 630 Early Continuous Shed Clearance
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # Late-collision terminal overlay
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(_lizs_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_lizs_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_lizs_get(farm, "hands", []) or [])],
            "market": [],
        }



_base_agent = agent
from scripts.v19_terminal import monetizable_terminal_units, terminal_market, projected_shed

def agent(obs,configuration=None):
    obs=dict(obs)
    if obs.get('step') is None:
        obs['step']=int(obs.get('day',0))*24+int(obs.get('hour',0))
    action=_base_agent(obs,configuration)
    action=monetizable_terminal_units(obs,action,obs['step'])
    if obs['step']==718:
        action=terminal_market(obs,action,'collision',replace=True)
    return action


# Online exponential estimates of observed price drift, reset per episode/seat.
_v57_price_state={}
_before_market_learning=agent

def agent(obs, configuration=None):
    action=_before_market_learning(obs,configuration)
    seat=int(obs.get('player',0));step=int(obs.get('day',0))*24+int(obs.get('hour',0))
    prices=obs.get('market',{}).get('prices',{})
    old=_v57_price_state.get(seat)
    if old is None or step<=old['step']:
        old={'step':step,'prices':dict(prices),'drift':{}}
    drift={k:0.9*old['drift'].get(k,0)+0.1*(v-old['prices'].get(k,v)) for k,v in prices.items()}
    _v57_price_state[seat]={'step':step,'prices':dict(prices),'drift':drift}
    shed=projected_shed(obs,action)
    market=action['market']
    crowded=sum(shed.values())>75
    for item in sorted(prices,key=lambda k:drift.get(k,0)):
        if item in ('WHEAT','FERTILIZER') or len(market)>=10:
            continue
        quantity=shed.get(item,0)-sum(o[2] for o in market if len(o)>2 and o[0]=='SELL' and o[1]==item)
        if quantity>0 and (crowded or (step>96 and drift.get(item,0)<-0.15)):
            market.append(['SELL',item,min(quantity,10)])
    return action

_before_compaction=agent

def agent(obs,configuration=None):
    action=_before_compaction(obs,configuration)
    stock=projected_shed(obs,action)
    result=[]
    # Empty SELL orders still occupy a simultaneous market slot. Removing them
    # lets actual inventory compete earlier without moving a buy across a sale.
    for order in action.get('market',[]):
        if len(order)>2 and order[0]=='SELL':
            item=order[1];quantity=min(order[2],stock.get(item,0))
            if quantity<=0:
                continue
            stock[item]-=quantity
            if result and result[-1][:2]==order[:2]:
                result[-1][2]+=quantity
            else:
                result.append(['SELL',item,quantity])
        else:
            result.append(list(order))
            if len(order)>2 and order[0] in ('BUY_PRODUCT','BUY_ANIMAL'):
                stock[order[1]]=stock.get(order[1],0)+order[2]
    action['market']=result
    return action

_before_herd=agent

def agent(obs, configuration=None):
    action=_before_herd(obs,configuration)
    day=int(obs.get('day',0));shops=obs.get('town',{}).get('unlocked_shops',[])
    prices=obs.get('market',{}).get('prices',{})
    favor_cow=(3<=day<=17 and 'YARN_STORE' not in shops and any(s in shops for s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP')) and prices.get('MILK',0)>ECON_PARAMS['cow_ratio']*prices.get('WOOL',200))
    if favor_cow:
        action['market']=[['BUY_ANIMAL','COW',o[2]] if len(o)>2 and o[:2]==['BUY_ANIMAL','SHEEP'] else o for o in action['market']]
    # Deliver the animal actually purchased, preserving the pasture/worker route.
    shed=obs['private']['shed'];invs=obs['private']['inventories']
    orders=[action['farmer'],*action['hands']]
    cows_available=shed.get('COW',0)
    sheep_available=shed.get('SHEEP',0)
    for i,o in enumerate(orders):
        if len(o)>1 and o[:2]==['PICKUP','SHEEP']:
            if sheep_available>0:
                sheep_available-=1
            elif cows_available>0:
                orders[i]=['PICKUP','COW',1];cows_available-=1
        elif len(o)>1 and o[:2]==['PLACE','SHEEP'] and i<len(invs) and not invs[i].get('SHEEP') and invs[i].get('COW'):
            orders[i]=['PLACE','COW',1]
    action['farmer']=orders[0];action['hands']=orders[1:]
    return action


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


# Local study only: source route copied from frozen v57 reset candidate
# (SHA-256 4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e).
ECON_PARAMS = {'cow_ratio': 0.85, 'max_seed_acres': 20, 'max_sheep': 10, 'max_cows': 8, 'max_hires': 7, 'land_cap': 4, 'cash_reserve': 1000}
_ANIMAL_COST = {"SHEEP": 500, "COW": 400, "GOOSE": 300}
_SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_LAND_COST = (0, 1000, 2000, 4000)


def _econ_live_counts(obs, farm):
    counts={"SHEEP":0,"COW":0,"GOOSE":0}
    for row in farm.get("tiles",[]) or []:
        for tile in row:
            if isinstance(tile,dict) and tile.get("animal") in counts:
                counts[tile["animal"]]+=1
    private=obs.get("private",{}) or {}
    for inv in private.get("inventories",[]) or []:
        for item in counts: counts[item]+=max(0,int((inv or {}).get(item,0) or 0))
    shed=private.get("shed",{}) or {}
    for item in counts: counts[item]+=max(0,int(shed.get(item,0) or 0))
    return counts


def economy_postprocess(obs, action, p=None):
    """Apply state-conditioned caps/reserve to current visible order intents."""
    p=ECON_PARAMS if p is None else p
    action=dict(action)
    market=[list(o) for o in (action.get("market",[]) or []) if isinstance(o,list) and o]
    farm=(obs.get("farms",[]) or [])[int(obs.get("player",0) or 0)]
    private=obs.get("private",{}) or {}
    counts=_econ_live_counts(obs,farm)
    crop_counts={k:0 for k in _SEED_COST}
    for row in farm.get("tiles",[]) or []:
        for tile in row:
            if isinstance(tile,dict) and tile.get("kind")=="PLANT" and tile.get("crop") in crop_counts:
                crop_counts[tile["crop"]]+=1
    seed_stock=private.get("seeds",{}) or {}
    money=float(farm.get("money",0) or 0)
    orders=[]; hires=0
    hire_index=max(0,int(farm.get("hires_today",0) or 0))
    land_unlocked=len(farm.get("unlocked_quadrants",[]) or [])
    land_cost_index=max(0,min(3,land_unlocked-1))
    seed_budget=max(0,int(p["max_seed_acres"])-crop_counts.get("WHEAT",0)-int(seed_stock.get("WHEAT",0) or 0))
    prices=(obs.get("market",{}) or {}).get("prices",{}) or {}
    shops=(obs.get("town",{}) or {}).get("unlocked_shops",[]) or []
    ratio=float(p["cow_ratio"])
    cow_preferred=(3<=int(obs.get("day",0) or 0)<=17 and 'YARN_STORE' not in shops
                   and any(s in shops for s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP'))
                   and float(prices.get('MILK',0) or 0)>ratio*float(prices.get('WOOL',200) or 200))
    for order in market:
        op=order[0]
        item=order[1] if len(order)>1 else None
        qty=max(0,int(order[2] or 0)) if len(order)>2 else 1
        if op=='HIRE':
            if hires>=int(p['max_hires']): continue
            hires+=1
            a,b=0,1
            for _ in range(hire_index+1): a,b=b,a+b
            cost=a
        elif op=='BUY_LAND':
            if land_unlocked>=int(p['land_cap']): continue
            cost=_LAND_COST[land_cost_index]
            land_unlocked+=1;land_cost_index=min(3,land_cost_index+1)
        elif op=='BUY_SEED' and item in _SEED_COST:
            if item=='WHEAT': qty=min(qty,seed_budget)
            if qty<=0: continue
            cost=_SEED_COST[item]*qty
            if item=='WHEAT': seed_budget-=qty
        elif op=='BUY_ANIMAL' and item in _ANIMAL_COST:
            if item=='SHEEP' and cow_preferred and counts['COW']<int(p['max_cows']):
                order=['BUY_ANIMAL','COW',qty];item='COW'
            cap=int(p['max_sheep'] if item=='SHEEP' else p['max_cows'] if item=='COW' else 4)
            qty=min(qty,max(0,cap-counts[item]))
            if qty<=0: continue
            order[2]=qty;counts[item]+=qty
            cost=_ANIMAL_COST[item]*qty
        elif op=='BUY_PRODUCT' and item:
            cost=max(0,float(prices.get(item,0) or 0))*qty
        else:
            cost=0
        # Atomic hires and land are charged before market sales in the engine.
        # This conservative cash gate never relies on speculative sale proceeds.
        if op in ('HIRE','BUY_LAND') and money-cost<float(p['cash_reserve']):
            if op=='HIRE': hires-=1
            continue
        if op.startswith('BUY_') and money-cost<float(p['cash_reserve']):
            continue
        if op in ('BUY_LAND','HIRE'):
            money-=cost
            if op=='HIRE': hire_index+=1
        elif op.startswith('BUY_'):
            # Model market transactions in list order; BUY_PRODUCT uses the
            # visible quote as a conservative unit estimate.
            money-=cost
        orders.append(order)
    action['market']=orders
    return action

_base_economy_agent=agent
def agent(obs, configuration=None):
    return economy_postprocess(obs,_base_economy_agent(obs,configuration))

def zzz_economy_policy_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
