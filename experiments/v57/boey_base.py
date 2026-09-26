"""Lizs (Elo 2522) Backbone: 6C/4S/7G + Closed-Loop Weed Repair + Market Impact Slot Ordering + Step 630 Clearance + Late-Collision Terminal Overlay + Full Seat 1 Normalization."""

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


_LIZS_MODULES = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rlKiFO-DlHjkD<(=1n1VA9=tJ#L%&=PIySu(YhJiR?69#jMhWR1Wo7*&u&YxM6MM;?(!6#&Yf+3AI6+9oP9Bd^HF$T&aTtEQ`b'
    'SyzL%hX<2YxvsOxO?FeRZYNciuBO-bj*@%xRe6(4Ci8W@US*R>lHV-LRh^_oQPydlmqm3^sBhD9d3#a3IDYvu86_Vs?#<KHO}4rK'
    'DCZaV@bksJaWA>JcbyiqiayiNn{@RitNHiGi(;0|lU24{q_>l0xyYxtopeh5bdN5I1pdJas-(O$U-6%+&X&;iO<r_v()XQVFUgA<'
    'D-Eu)x^r<4%P;Qrl3_O~SMcv{FIi-TfuHn~gRX_P%3#U`&1x{qvL*hZ>z*U1F+#z4sYa>+kL{v>j_$oZ`0J$3RxqM;fvb5z|95&>'
    'WvjQedi}Ck+$Oq8QohYrF!L%|SJ^DNgp%tl0U$|wxuE(9@66z$xF}vh87%!GyU7aPizKgb%J36@qzizY!+I_=_*YRU<s7!{RxNH)'
    'uhMBYNRp?paVbE1w@R1L)i=E)O{VMB3R?7UvN}y}vRRqWdN|n>HvKwVCCl|C%n_ERs8{78d6(DMfIZ2ZqI{PZS2*a4qFgS^0=vzz'
    '^Sr*rG4ldIZ`+`ihgj;zO<G@L*+ud4<k_?1@1LE(mUnmuF7Ca2b$0ys?@!Lo{(&2Paqs!bv(sPHpHH9t%zyp;^z<43b@Jnn@P}^v'
    '>h$^Xt5Ys{e0+9x`byRR>Eu}b`NPTCtEbPN{`<)pwS%31ad!IT*T=6W-~VHB{L9nl$Ilq~AD{jmQCfEU@~4xN7yQwV;K$R`mnZy@'
    '1_LMH$7jF3n*9Cb>5o6XB3O~B9VLf@p&7TD<Wcfy@Rj{Y{kj#oTda3zzEQ77$-&^uU>)%5BlA_S2!0hHd2QT}a+P!mOzipb|CyYg'
    'Jvli;0&y^e9sKF!$>j0zi{r;nU;Tr=4S8$vj8BU7&1JUgyiFJDtcS-wT`%g<a4^(ozFyrP$@5x4IY5~&%CzQY>SSi`r`fVjI<Ib*'
    '*~w~Eu6oJ8VKM#PJqpge>dQIS3Vc2%3>@UuJTLM(>+tt(k}aytHZ+r{uCv)Boldi=>RguTYBs6z-!t9kb-I|th;2dg@L_W3^!ve%'
    'u0z#<O7#-`SGVUCw-niy4XyO&k9Pd&BEKpoM6ng^143Y_E+6RUX+6CrQnkq6W(n4YGrNYfuPMVSyGfTzMH>>>ntYblK;f3FY@WX#'
    'Xu5zP;jrgWGKvyjBtjoPs$E4g2E+)^26x3J^;{;2eKNv|v`a&7kM~mr&220Cf{o6{)ara}Ya(J{@i~JYW1ngS-_kWgr3w!|eAI}y'
    '%%(L>2dhvWH3!wDx(r2^U5y%0fbH_C?(m|xP2B1*8tj3}x-cT$vp{Yt8)Wa{ewcO6?VX&=0T7U2!11)W$~tDyeF3toJK~|7+v|NC'
    '9i%ShQJTJdAZjiM<D7t$s~N1Q+lB_n1u#fza(<*oIUai;H9z6O^q{z-)ot{ej-4aORqdfzuFC(QzUg!$*1@Go`01XD7hDfk@e1zt'
    'CugTG9=>>X{P+aO#ImgN8k)Vk&f(}}@3SdzU&&<#W6bD`@Q9p~@jn3Hm#ZB3n#}1$eZy`5?HT)ZZMBZ}n!|tIWVc6&VBm<7D~`?9'
    '!rg?Ly@ZQlOK17C?x@~0#|Qi4ble>P&AzERT|?>U@Dy)>M=4i%W=@<7M^uQNRoYEtS`g)MUA#j8EnqIgF)*C>JEA;t_|*<5J`>^b'
    'pCLqhJ`k!?%cBqqW}Po+eqsRhDS`mvLSo8A6{*U>P>&GrG$?Mm;_$TSjY2l`eJ@$VjX6=295yV28$MgXD*G(HB52eq`Hn|m)|f`&'
    '6p7uD5SS_e?^&!f`&Gk%ksFZb1a9nf4vZ+U(|J+VX)(=A_r0Wp_|Z%1HE`Zt8jKts(%!?3gMhWTg#jRT>xSoq9?qA8an~7A2b*<y'
    'WQE=U=pR3HhRL@h0Q#-mF1(28`+NEQ{C3>kyiT7dFLRhUY|>R;WXK5~4!-UsxY?4F0sB)f-U40;+V$-8@y{nu`q-I-ceMuGfEUNB'
    '>s6K|Q`oW<kVOR8S94(uz09D;WKmAv;2Q|IhZNveP_~fJn5g3J%#g3JM-cH1Mgdf*Tq1Vi$3ffH3asqW;qU526(t+jOC#Z}OU$+>'
    'Xe~rdAh<%+C^ZulP0dtH0PqX1go}H)dBB#t9qSv3kWx(~1fDG#U=l7|+#`fTJQH=gcuM^ffsmmq3F=_%RzX~VDjH+Y-+SdLJP6ap'
    'q^eizDLx{-XBW`MSHGT}1TQb=yLfy(KE+k}NOTcL=WPt0KKDy>4DkL&y!i!QzOmXfiFP=%9_?>8UKcAUI{gNA9qBnNw%=#G?ZrK='
    '2YaH(g?k$DAD;%q@j85H*~ijv>#XAI8_`<s<{{iCiY4`N;SsY82QI*^pJ?qP6?ojCee6kbkQp&iT8-v<%aM2Lc6$!KSJ}pcPxl)&'
    '|81R;q=U|_8i?0?RhEeOYCP`yx1Ut&n~q_M21Enk{P{#efu?o$WL;(iTE2z-g{W*GMAp^xe~yzvCfbfju2k~Cf^p?vy1HeUwJc}?'
    'OnX@Y(sqJ3<OvY?8)O~d!V$TIqi<wl)q1&H+?uDP7AN5pHM<EX3Rt!O9$wkVxir6g02?WIX2B{WAq?J!v>r&jaAA*<;b3Sm3h_t_'
    'xjtHEYE{0Y7mVrIc~FKd-I0r{L|E~$hhXNCBEc7Z0n#YX;lubSz#i}V6m)FsV>(@xD5(V^))7<=zcOJ4TGt)GzGtgWh`rPp*+;c_'
    'kzRGtIo2H~5BS8PAj*i9M8CIrwwO(jPF0K*{)uB+8V*>~*!CgAftUfUhUS5+kl-+saGt7N+w@cwnjy>%&Lk0oyUr6j71ih23Vs1A'
    'znY|P(|nP_vBY*iq<|dVwqdyvKs`E#O6a;mRK`+ecsyJcDc)>!Y;->)PpTph#bNLyq{HEk&XM6t(XJHvHpz~CP{d;hwnA_cJ)gs1'
    'wt|GnCnrxFVD1xC9_&y`^grTI<2dGsV!Q$3ILmXQSeXb^=6StCMgZH-mzsfLnHg0g9aua%r^<|&@p_l5EPdl(tU#&lWqG}gjn)Of'
    'bS7|j&sK1KH$$K&XGhHd5Pd8$zA9I6=c>}KZq~KuYr25jVlvCs4vQOj`^(O~&)k=;S|*mhqsU|qTgJtUY>wnFe!?q!`Kp!9uddrF'
    'ng?;XCFy0=!EW$L(q}*xF8=cX7|;8*+JUWh;8sH>46CJ3;gY3>X)n3NHU2$ca_hr!Pc;Tcw;L?A=3OQ%#gh_3Xt!QuBRC!90!}4-'
    '!DYVRW3}8g8@*bsGnX}bnJpGc_BMm3rInZ|%Kx`ydR><I)<wZ4K7>iLR<ec>`KXXLQUaJ!qi~<A(Mx~SChRmaziGw{w?!Z=P<2Fa'
    'Mjkk2VrGj1ZYa(%>S}<)Fjcj>T4Lu&z<hzO*AmXz8}}}u^#fEmV$qVv-n0112#>Ac${UL-uMzZ=nrb?%U&%@?O>ZLn#$(WLYUKR%'
    'mVMO1G$7t26dViLn#U=MBWa!kBPo8seRNrQUlajjH%-4CCBw}^HQduA!e#Mhi{1|4Q35r*-tbKDtcfrO;)!Zn5?XLS_s!@$(S!w~'
    '_oWe1-@yejK-?I;l=#Tee-8)=ST@l9MAThG1O^>u(lk=bT^IzyApGZkBDBGB8KHWtHZ4%BfRvVt^6Fq|9*G_RY5D+IHb|FfIMC_P'
    'bb3iYwh%q<<*TPa0PsfYtdMY3imWNZ0`!cK_*^5o4@Rk^diek0(;9)>`$*AEu?I>7;c9}Y)AJ*%f*uDq7q`<VEnNTyFuRRY370%r'
    'y5LfSKaUs$J=64D={W-R$rFONOW@(HV0jb>JzXPm<~2F;MK?|-8gY0+-b0E34APk@x0i2p*F4aX{R{R^Jtl6-x7nmF-=(XWklokm'
    '3eFJRU@Rb46H(H5UCp2t&RVqy`5dc%QQ8%%s6;ZRA7IW#i}dDlmI8PnzDEi17W6l>D({iV*l)y_+`_@qKlNWj!)VknUZUyTi+UfS'
    '92}ME@_NAc9E$$mi{aaf=7i(p<Rv|b-m{H>ImZm(yUhSjjx~S>0RU7=+-?H!%jwyxp9lhO2AVH85Wd?C;pOSC0>T3eAy8w9^P@Ec'
    'y`+F<1<@A^-91pGNhxqW38GQ16u0sd3#^OV@p<unoP36dm-QjRRiqKg48lceiC`M7Z-6PP^WTxNGj?VCpm%vpG*5Gx$WtK0t9%BG'
    'A{v}w6Qg6SuT!!CV;u{0pDJq(;s7si*{<&EgKzG_MZ&sKb45WqUmtwkLs${38-0fVDRtdDC|@<@!Q%E+itAu4qW@{?=}%Rdi(+k%'
    '^5LUzhoV?kPx;#qRK7-xB{U6xoaQ`GVs}>QyNSJ0j2@xuz6|iKXolTOoB<!TsUuzRac#4#vz^9SsJ%OQoFoLRdUn1Zj3q}3&w6|g'
    ';_J9Ul}U?aq%a+;5LM4Vqt6KR;O@;E*Zvs_ytR&-kE^ST)8Y?xPvgCdcV1;~VZ3{)Tb@e=!>ewsuH7*XCa&{_1^;dz$a~>peFx*h'
    '(V3+;fP#xa0z20#+OhY#Ve{q@P|vTKYm}YXi2*5Wh2Ov$@yIl1<aO;mWyDB)LAe?h6b{3pa3#Vz+h|Cs9$;UaY+Kz7-^p=wH!b{6'
    '$7laWtdMI9BI^kiuLn(%AFZYz$+qTcp;=vNLg%y|j=h?~PR^-#aMaERr>HxdD6?|r5iZjzGv*FA<;;^d9h0^VW|tJ{4c!06@?0z6'
    'rZAQ(ZOVyO<4fcc0I0Hjcen&?lE0NXehXva4BFu?a0ZA^AK*gO9FcwfqvY6pR<Z@>n-If&4Bn79@?AJCm*t@Y@{LRD#b~F8!wGY*'
    '-jM9*KYAEuM%5}{l+q6?S7fb?cdltT^uY8N>5e^{C3eJ_n|l@8aL1k<dFsaAc?$ruvx(DCe<N9W18%VW(GNJ5K5M+!D>xJt@IpwK'
    'uJaZAH6>RD^lMnb>4Wo8yn#`@V+*L`+J{EQ(`i*JQ&5uJD)A=bl9>@!yrHAW5@8>X6%eCDfWRQK;?bKf)?_JF!LjCX3p1{&E~jq>'
    'f6mH#d+skfEgBt|??%a2-wb1?@Gc{e2p=7SzsLSS=yybGg3QL@pE1e?8jdtp`$F-5T)M66ELl7sds&6IfbgJF(2R(g+bD?a$7CGE'
    '_Wn$Jf2O@Z)83zH@6WXNXWIKS?fsed{!Dv+roBJY-k)jj&$Rbv+WRx@{h9XuOnZN(y+705pK0&UwD)J)`!ntRnfCrndw-_AKhxfy'
    'Y46Xp_h;JsGwuDE_Wn$Jf2O@Z)83zH@6WXNXWIKS?fsed{!Dv+roBJY-k)jj&$Rbv+WRx@{h9XuOnZN(y+705pXtBKpXu;WO>P31'
    '4Fg4|rq4fnxUN<YFZ1GIR=iD?w{TAskF>YXDT;aeRXW!Q-RG9td&n5<B>+76Ila1C<<s?o%&Dq+J-ao&PRi@(?cu@TAW5(AGDg`g'
    'oI3O)KsF&mzXP?%d`MC<7w^AY<u$xAE()V!U?D9%*srr9L7oU-!l+6?SsRPK;7dtEo3BcCpu!*15}mH#l~<?}`rA5NXJpt2%mJ(='
    'N}=)C!*jcW-C5+9^dx|5wYo_c3wTwMmM&Y(VI9^f3GOb6`^oFqyfl+)QP$P#*L>9i40aNuuF1Qr!l7s)&*P;ge{-PFpaIIdqN!zc'
    '^3}xAtdi#p10o2<g0m<KlJzpQBFo9;iw@6pm7!P!v6mW?Q<xqk_F(Og(ASI?(d?gcj!{DV>3W59F<YR<8Yw4C2u6)J=?qp(ImW>T'
    'GwzY|$6UFV&FA?vPZu7xu!*WBo6B?s(}hK@U}t{LGV(sjYqTqcmayn0)O-Wa(*g&c;ag=*)<%~%c|{16uIe0j$akW9{rU~`3;Y0J'
    'dk$-itR3vuAMW4w;_T_;lgSUyPEXGg(o;V_KKuFP)#SzT+41w2(lyLDVRa6_?4cLc5SXnm@L#}X{k9@K+;H#>U2o+T|2phOJi9uN'
    'MEftP{WYu`-RPv(k?_9mMm)wkUkwd}!=VddIQYVa@Rfz&dbf2B4lS4ie<EMgMDij_S3EEQ$N0j*Qdkg=7=)cX1H>PXWNYON*O5&h'
    '9mXaRTSx73*EtZ2aBz6&O}b_D+Ci^#IF$4MvU%{Ld)Mo(b1)2c!uG0XAwP84OV5bVkxN(3cVv^SJ@D}9qc0g(v7ue{JhKsXqfjaF'
    '{t}#f_d#h|*Q;2+UB{~~U1lA8pd6vOh_aVHV&elKA#lX?ujD`Jt)^b--K75=e^=wvMkmH@N_r1kh90|8yn|Y@hWSNW;8r!%PVTp~'
    'LWBw1ks=QZ9S=u$h~-sdOI884H9Z)%HXbS+W+Mo7QrveB?FiC&+6$De(1(a}Ib2Nqrzlr&b>_d5Ndhn3LxvHIR8)PCd;?>>Z#P$z'
    '^+|`C+`n)9Ez=w>e`|EynWJ$I`ZO1Y6-Ts7KHywGTYV(+79*Kwu88io4x4fkVj3wJ8Wz-qey9eLFYYrQH(o>03r*jfzpcwUW3@$*'
    '34enHTwV+3)s3&^UXuN`&fz9q<?9=DBzk<`!nIUP_1~;S0zUN;#X?-de;bXKkp4JV5L*Zv>lfp-qX+h_9D-z+fq%+@wZn5K2LU@p'
    'a)gKafXmUU3DAGKq2&QJd>}yI*FZcarvNEN2k2nN-SZL4JR%%bznq1$VE!!R%5F1@{^nUokaoTMku48qVb1gWj$km9_!rpH8QW}-'
    'P+cQ;UQO^hsddzV!<S{bIBK%R3RT^%6kDuesQh*do3-F>je{{h=^gA0tg<w7jSMh9g6w?cm0+AV-`|?I32)FWy@7WJyzO;(27axx'
    'Fbs$rapFKQ2Kp^UF9J6r!yFzcXv9<77Yz@rkB=Dyg`Tae9Jxw0Aj4JPPdX|zgCYif_1|<3j4qFX=fr^>GG$a>G2d+OJK$n3GwLf{'
    'Eplk8g?sRjLTwDqs8nWT?9`<#vi?%J>MuvkU*$JIsnQ}V*Ohw54&<Ub3N9C`nk@<Y(v(nn4xx>xXF%XOsl-j6xQVsd+chx2P+Kt@'
    '(=+0d2$`ZrZ?3xQRyW|9*v1q^{bQA7o!2H}L8puW7&#`gKb$tT7xYcp5Fu}<WUp>}Mk*ai!L9<q;odcn;NI(nqhP(&(77m31heuw'
    '+6ETT_`ujmqKhe%*S<TizU<uLD$}_ZGIv~mZWCJ~7L=gtalu;RLu|0CGiEr0Dy!9{-lUjpt}d0b9xkfto&}@?<(b!z;#Qjmxs%Y?'
    '=II~VgnS%{jA7StmC-SaO2JT!K%7y6^jwNNtWCJ)irBcx5pz`NFi+Bz3@MY=LU2taJ;1`%EJ#?miU_lVv0e7ok(MP~Fk!wn(RP?3'
    'jz-h<(o6bEbL=7ymv*<cG>sdWN(#zFuBEmaY=gD7-aBVvjh1_OLlFm#P6R+krPqRKJ$6+yqj00;)1b!Lm52`bXNP;}`cYl{untA`'
    'o-84$Z8uyB##3HJ$4-u+jH6OvDK>KkNkNZjyBi_K@3irTd8qY#pn8b1nQhM!b<%haAMoG$S<-SmNu2Bmaap@2Ma!FxXq{oysaiQZ'
    '-@Aeb5$<ckf*QmG?Am@(1I=dQyRm7ekQ!DTE#@9-59M{+pg;6faQ^$!4E@}U+xG)0SNRpW9(vS5EEA2?>u`P3@vzWA6b;oODKY10'
    'IYPOX{xA(mixFJin-T8Epa<JRT|`jzvr%;TjpRhz9g#j*B8&Okbs43Kp{n6s218qA%QRov=xI-t189GaVFa)Wi;0yQhN~-Qr1#mZ'
    '504tS^zp*L$Z6ac+8uq8uvRsa@!d=_tF{)r1)3_5ZB@@$LBzvY-61rDeu1^xmUX2Qz2<wL;&r1K-)(tdYtJaBhtcGmbD}I1dP;u@'
    'KP@z>t)9EaltH^PlZygs)A3}p`IoHMCF9Vs!(PuBJd<(FPlY3Q?_Ump*J2zNja;O|GRfAVotz&&NOa5Li)g%KJMwR3^d@GqWX}%m'
    '7N^4K1KlOp?nJi}T*zwl4emm@oRkI7h<bWGa$Gq1AiN?)VKPqvb1>{izL-4(5JlZDi$0w)*q9P(T%wQwe)72zN6)-^k87cZgBK`2'
    'AbFxsp8kjmnNyZ`;XR(vBIOt)tR{m(ETA{@Ona7V?vYe=JTqmsN<jZoAw&2!$493;^V$@UT)6bO86vx<kVXk9AB^ZZ-{ZOsiWb=C'
    'YF(uBIqTGU3K))L4QsKUq9aZCyp>Du-d?iASSQ!YX#2zP2rwF+W%!?uv3s_#KB(fxm7mSBN6KdTmBx^;5ZC^;t(XShSdL<ZTgI)}'
    'u(J2doNgJ5ERkB5w-aLujis;{p7&FWruz<tM$Gf3_1&$E@t-Rae5-9dM|fiyrsg=QmMO5&d|ZH4OVOYZA6a#d;uFTPDZFX`y=r}j'
    '(4j#c?KE|x-lW>JlWnrJcxs-nD%FbgrYsM_I2cOAG|Q%JdLUqtUjeGEQLD?xiQ(Y$n0ii9RIX1KSz7QsG2~&60(9#BZxR}@u<wvp'
    'ef=8i0{z0BewzUWd;J<k|D;!i7n@SL!&9z=ryMKtDFmqnRsj(zYLu4YC@$0K8x%(&J#-`aG}tA2riZXdb}-r!9mg0{BLLr0nL-0J'
    '%9&^c>K}BQjR_SZd~n(vsq4@7FHW}|w#6NQ5RPmMo>eWm=$gEq@UJ3bsv>Rc-1|xJx5{u=8r(_SdXBBvVqovJF;@0GQDm7B@tQ5{'
    'x3OK{-e&!ewGeOUfOlDKqC5g}7wA61tEA^}t{C)6JF>pbbo3=3%{cNI;CKVu!%K*?j9D)9gbBR;o$zULQDT1iYCOww*-@h=O=?(C'
    'qG_DuH+kI00}7z5opBg=J^={dMRmGzUm%(hyo#DYH{0h1Orhw-a3S}`8>Z{spS#TyhJA>tP#pWWc*i_&c!+3_9>wmAHnQIA(Z#qB'
    'jho<bhD4mB3pFyGHbhp~8chOJahZp<s0{J-Yu;Qv<V~CBayL6-={ED;{%AzyfgR~@!Z_LPZsMHjZfH_lvUJA~4MP*~_S7T<fA=HQ'
    'gWKnYrgkb?o{%2vL3;7@^yjTZiWq*7U&Ped7{^OTRZ~y<nO)rb{@16^o=lu*EH9oN|MDsxe54`p8M~oGU++7FP)SsT7B89`IR|oF'
    'n4{gWO}`(5P=m}#E9$72k5~;$*^WF4Xz<Hx_i-C%2lQQe`eQ(sCHBiFO6;J?y3Ug&R@p=alC9i##5mSM_*~KzfZu3yghS|1U7Zof'
    '@)o}hFY03DKjtIQHu`o*OWsCjORlP3M{P1UUB!E*%AamU_ktLa?!V)F>^55tzdd|3ApUle71MH-t)giVPz8@>wP<Zw)kx5;;L$?u'
    '*b|H2P}4<O!RvlemP_-Z*<FxFwGa(6wMDAhV>ZfF6=rFjPJx|9<5^X~d{R~FTQ(}?(&OS*+ig;mua`0}fet_An_Pyu2cnq_JnKf+'
    'UeU8Z^o$9k=7F5L;QQm3ClfLPi5in0ei^Y4eH2R*@YS%vjuXu|1ItV_%=8Q{#TRWvdGJ-3w*bu;8*&T`RgQs|Kb^jqh#fG~`u_Om'
    '6J=bg*Ue7W8d1J@`tSdKJV7X`s?FaZV}%9nzCZi*m&ZR%UcOL<v|%59h%wvtAIE3EOkTb^Jv&iN)y~-(Xs7e|?Bw{l99a;r%qF-9'
    'W_9vv^7!}%4c}m&u)lqNdiv_8rze{`5C*5mXU|X0UQXETMvr~BKx@kAl*8fajr-&j8d_dzOjwWbc=kAA9NFdlzhlh00$O*Iq1y3g'
    '0(bsAzgqJZ)Ny{%49Hdq#;*sA^y)1ss_?;wqjB1hTUq(8c${HHj3f0_wIIvmLk{SD=#Cos;mdS^YoHlJ)eGvXzTgY(;vU9dp58i2'
    '03??6WS&vTu8R1jBgFv0u<?&`T6?n882f?!6#4Ch!Jxbnp>%H5cr=H|`%}W-Ay=ndmR&wC%7Dzdc=7@N{jq_&;V79wgv_Ssl#$4k'
    '@#vY+Iq6|xg~<o}_s8a^P(y&t-j;5;;jnnXtpih$k3aB#TLxzXZn|WpIojsNh?|X3H$QRO8^dkx9A~pBdCdL$AJ|@A8o1NJz|TED'
    'e4-XVee5|P=Jb4}-X{d_BNE<CAWgih2vEcSYA{+F*eq}BI?YAg#0C(XLM*!Q(Bt>k!V+*)iQUgIUru!mhi8`Ez@R7al$gxY+l~%S'
    'p$36fsv~+BBRL!^AotaOp#_<W_w+{M?ZB6o(g~r$N&}~=3DV`Bj@kzU&=gyj>cT1A175M?AAyWv3$bQa`?0b?g)#JD3<=M-$C!g0'
    '@oc?Z<Wq{wd`+=>nXFchMHaWht6m>F6Z}{oU_c$s%9$`K(>L_qlZ%i%)W^`7y|^yaF#JuB2H4aif_6Aa+Ig(pOPs(JWNWr0(^(Aa'
    'tgNjx6samYaBm?oHC;Oh#gFUa5E-8JebK97SiCLOE*3Ial2?N+@m%vAEIgJsK9Bm)!I%xp?sd_1+B!>hu(9V34GzI0yP;%JhvM6T'
    '`gS1pH-a#(|B0?ZA{XcBuyOI7CAc5X$|1Pip6S8An)hM{n7iMzLYvajx8$XM=f1>e?vag`K*!Q02D*=%G%qk58tsE9VP&OL)sPKK'
    '7oY{%aq__)3<hICGgQ=Eaq<D!SRPeNbA0L`?I$O~<E6D8+YvWa0<N{ONLivcm18WV#<DD%Mf<c0=J_HOOl*}c=4}*_2DGk2Nt{+Y'
    '>w5$N4cM;5uLx`E)q^i#HE;X9CSGaSJg+9=uz78x2Qo5JP1u=$x;HM*5WnjvO;uLQug*pL(WQ%;LOaygJDjl2$OjU-e!zc!WT}~4'
    'V2jFvbO(u}+UbSpOJTmgqQVZ{qcLCud8*qB89oKnoRAi{{$bhxSvwGg5JUu4)7%Pv45e!rDz)~983{7#RHw&hv=Lkxk-i&tIcr;Y'
    '6U27oY6B&iSe~^JAXMXk<C4R*wOimXms`PCRBMM$7*jDrqT;11Qf+i-PFPzHyxT*`3-n+=s@?+KkLJ#mlEkpIg3)$ZY8|qD!g`9>'
    'b40Df2OjE2^DY>>xi}dI`DNftQ(c_^#`4iDES``A7;Oxc{3eu$NWb3bjcOtZY6*$59uDn$+{l5XiWl`8%^PlV;+}U8AZTJ-Yn8su'
    '9O4C9ADP4<YSi(}BQC%(E5@8Yng?T?AGYylLYb0VwN@AzdN8RNiE`x|gCr^=E^nuN^DV;~g;nV$ReEpCr22)^L|=2;irl(_bt2{$'
    '!|!8nI9u$_eNM!X!+DTw64Ske%D#|}XYfTg^7d;5hZSFBt0%l5Y9S84=tduc3X-rU+D($U)q|od4eXQ7E^S-^rF+aft_|SGQ+dKV'
    'jo^PhNp2iQX{1aBzdraYhW_&yG(K-5{*MC$$35czi0_05Bl@@ZRdFRFO6aB~nu;%y<8}CnQL{Y3#AQS}#c(`!Eu4DW$OH5mIlsJ`'
    '4qlI(UtUcQ)kfZLnGi+%?Xy3l57C@DN0DUD5k60dqB`5SU&iw4g@a?x>dzWkEKNfDu;6%(d>K4mPI6uKeGpVM41<HV+3b&<o+AB3'
    ')i<PO^=C&fw?A(*2z}e(bcJdg9iGt%&8oFuVvHyDLDaYE3Vpuek*M9qIoj1Djylw@SNYWydf_0oDGC!Y30=p1?{U;qq{(~@J&;MI'
    '>7T++X(RgzEz>ay71O#ZNiPbUbh}(;1?$k!u=WzR{ckqHl#X<<zN~I5$}CaQ@Sz>7B*w2x-d$rPEe!9(?%^{n$|Iv7?Wap~qp;E('
    'APR;}?(x!o`3@nIw$RNxfs`VO`sbXA+&c02CJMTuej4`NSLvS=oym((G`vH6CO=Nn@D350JQ!aM?--+L7=$?*?i{6Q=!9t+?i#15'
    'c}2I3)YLkM?P4`KQ;<X0F<MjPiyyD)PYjCG94}}e4e9@rXh=AvPmOo9k4v<VOY}#^CF1Zq8T(u}BB9M5WO0)9AXJEI4mTAov2Lim'
    '@8k2Hgb5f7p;+7KTTn_tMAC%_7wQF^;1<Rk$q&k6!=qR|R+#-jX7%kl(mWkIB@#8o2QA0*V8kt@yVa=<sHu{@&&rIWoTsx{^1lv}'
    'D#hd#b!mbf7^$?EGYm)cUEq8ng17hv3Tjkh$aZ(tv$rfr_tx<h=$<OeQ__fCjVYQpsG0u>bjF{qpk$BOGk&{hi?f@XY=(}D6SZ@S'
    'q0sKCGKjcSR9<3S>in(yl|xNU-1F)bIY(C*&GD!vh?$e=b&0s|+EG|?(4?KTMi%gLX6q2!RZql3Dav=wH?5;pzpu+x{ySo+QOfq>'
    'CLbQgHd=Uyl#7)6nq)8tU2|_Ew3O(1Yd*^>5;4h2fBo{0H4BNMgd&=_<rEK0V+c_Vc+##bUi(?UF8lgHtYvT}@HoSI$+^BU9<UoY'
    'd0LVIID519*)Uu!6TTyp<Ov`0I=@jarfPLCI*_Jr1-x>JUv)wdqdPah)~z?~dkmnC=fBG8h=+G5KJ~xsD&f?47N&I9C78`!dN(^L'
    'Yf|8t)$cj?O>j~6g7eTbW9WL;2A*5B+cC;a-FAd(NU@<^D+!l*xaRYU?v?QJb556g11eF0&>E2V7USs<JaIY68_04Lh7)c)aa}LS'
    'i|q1W;#NnopfiFO8rcPMl5lSB#<#LzUoFaof`Xb&rY+657}4puMmt`<zcA&cRmjMZlLlr3?5(YRS{Bs5>I_NTfkkq!E*Z>U(^cSk'
    '?UA_eb>iHy4waN~G5yPP#9~YH-AVTB3`o^<KRSY4eZK}U;W)U>L@WRP9a(Y^RMJO&WL6=}F@2d;>Q2_Ry<3_5Q==E{yS$!WPo`y6'
    '$8Nd%_ussOS4^cZBEi2C&qseb>pmWPNt7x2j}2d90z@L=p-d0g_)G$l^)^?*6-ab=of$D{5My@|k22{LX#(OTXjI9%?HYS>?V+bc'
    'aUiyp;hFnlQ-wpXLg$fs8w#@S!TIPa;yC)<hcMjcQIs>&H^j(H!EC5!?jZBL+7)y1o&qqA#=>hJ%L*w5E)sCsF?z37oX)w)Jv%T*'
    '$*t8-@UC!jBacSj;u5J+MjsZTyS`?wkD10yqrSKH5tW$xM%F9PqmkRw7u;f`;5Hew4X<lH9cfv(G;Hg6)(P8G_L=P{OWY7>_i<S$'
    'KR{r{(4<)9)S<W~JQ19k2*&GbRh&~<mo@QYUO0C-Y3J7MB6)PtNH+7=z-=4b8y)~##vXoQL3wP9)gW=ajR{Ie($%d{BVooAC)f)T'
    'DK&Kp5nOX*BUB{m=w_c5)a=fFkG<q^%GriY&y5*lbTb()v!~-GN{x)xZ0QE!-Qq@{-K5R2hG#v;yr`FuoUzd+M5%j@U$Roi#upP_'
    'y*=s1a6XpCGx%FN2n5kbtz#G7Wcz@#y9b=D;N}LR$M$EFMOIwZ*By$t<e2)B#|8czk3G4xasX3J!l=*At;f+}sj8pSl1E@gek#xl'
    'I~f-V#%Q=t!B|~&Kw9XXMJ8VOlH2w=+Jf>6@3yDzR^teyZTwxRjMV!qo&CqUqI<&zul3A-R3P_svAj+dgBH+po%p^f60S{;M-@@s'
    'VPi+M#{#DoB48T6X+0A`Z^#?tg>M%j+?U!?cX8`n8CARMi5|^;#O)(i!|GNU3`N#nKazJC1KWmktSZ@!*SN2SrLkd(xxj9*?~0@Y'
    ')cm1pj#_FSpw6ocd~q?oRk8`n1LT5u2;c`pk4d3DzMm)snRg)*9(6HDw*uY`<3|(MNP%ZH>vE|%J4Nxd2dUWhkrG!qE>#N41@4;1'
    'g->|Z<%<^v*+j&$Z0YdRI(nPVm}O#v#3N7t5rL;=cK5B~MaNPNHypLNYpXug9?!fx>5#h+Izq})H)*RDIcy*+f)z81WwOI7E~7ON'
    'cQ*)}y=~C!Edpk9aO-H$?5gd;<Ve>lD)wFDTsK^sXl=xYOi`0O`_z*b^8Jo)V(g87_@#a219<_i?`C2o?9^J9PSfgoqE4REzU?G`'
    'ub%tQUp($F@;55GpP~JXzLeOPwnYoYL=uk5NT>g|ZlzP+q39T%CfE68PKH(ZW?km+0O<2Z&@vF;&SC3u2C#$LmGSDj)>#9WBoV5W'
    '+&jHR`7?^onU~hl5OZzCg#_vQU;pv&r>AEp(FmlQNKU?W+yND)C@wCH9f%!lxOJHBZ{3}5g|Dt&m7g&dt=a|!F4W<6Q^|a0Q^~{*'
    'jRM`>G|ip3kh!|}wU>!>CPu@HZ(Zze?V7P~=G_GGS?o&w8MLOGK7Ebf5X~&s2059}YZ+CXs^&_)1p8&2f9x~fq5MiZqO&wKN+snC'
    'Mg+_K9#|po!U1})T)oMNezpnfMr|^`n5BC_e@D)*o*%zUs$xcZU0u6%VK2@VqE_RAtdGRsz39D6Q9qRc@4G-x;^E)9KBqd{jBYw^'
    'yE7G#*1OM0#25K*Yoe$?_e7?W#`kz5MZF8%`^?V}9y#s1y3kzH@!4c-eFvu>`4rhchmlT{B6(KYN-623^Q_FRU5Z7tMaA?J;i`!9'
    'wT3Y&K6Au=E~HkiIw9V>mP|>`>rT(lu$c_|zH78YVip&TopM9|+EcGYxkKbA4;+q?WZ6dt!*Mh3_pd^p$Ce&vD9w1r5=f2kZQ>K-'
    'ER7-};bg8X*(bt_-TGBeChAd|*OLkRRUi3u0sUz?*`eBVc2D-@GEI3=bcAUQgu}ppkbq@^6y0x3d?Y%?+nIhk)7vl_;Fzd!GAn5='
    ')CoziS7;2kBCC0hV5h}0_qvgcDA=*4d*$lL2wKn2N$v{&8lzBQ<%op1x(afPapmO-P=tB;L3m=D@X@MW|A1=u4?fB`h&Vh7+Z|ze'
    'oPb(hl=Uq=FujoOTT#?l;ujIn+sun&Pe-)ZcF9Z}Zn;LD&y@?#1ln#G$tL9Sv|4(zo7qXfAKkX~z_ibl0QhRLHBm|d^4xDcj+!gW'
    'OOhH=au1G#j*n~lrV@E{od}zVRRafo?T;`RCe{|36!xC6DwG%Sv?+02BH<(Xc&R}7s6v55#cGj1U565ANDd~nAd{Qy27>~qL^Z0R'
    'ip!}}<OIqUkqtyQ@w0>o&4{aQvVHgxw@u2FZB!;3%nM)ec0Hzs3Rm@@ZR~3$1^7naX6h9>X_Dz3ekrUGFp0^8H-DnAqho?&^N5e!'
    'aR3bGw~fE9VwM`;DRRHkmH}+$hSa@&SE5LO@oo;&q2vYpxHp1?`^htkp6C0svl$xfDjTTvmBtL2hdyo#Kl0#)8)!H$&XUg$9{u$T'
    '9}+K5UyEt`T1*#*#n6ZgP~5!E(_lEP=Pw?UxWlo^OD`*woLpv<5f$g3uWX!^{uQA068gL@7c+njcVRx`i~R<c=xvs~%kj7c;tR4i'
    'ABD+oBmoeIq7&1Rxn8yL8odA@r_15B90bVdD&u#}&B6f_Wnwfp!-~f2#tLBywVq=bvH9}e>Ehn~(%$vLzSCvBMJ|j@*R#ojfr!>|'
    'lUv*|M!-%6c5du>Z{K4<4OuEaQX4jiQ$b;{6&mQtE?q=y>(8XSji#Fm^fT5LO=SG^lmT+YBX8Vy$WrI)o~;5ku9a@gRmYr1OW16#'
    'pl%U`5oSxAx0Yf{+*@e2P8Sn}Q~D}W$CkH4-%I{Q=YHSv(n4{#Xa0s<6uGWgM__Y%8B4d)a|CfVPh_>uEL)ab)9bfND2Gr6E#Ky='
    'vOvjsUmXWBxl8dmjl`ciE6Tjm@yPQUuA4rk&r!jO5`90eE0qrnUN|L++$lUbyg~cSlj+R9eb}f}JY4_A8OMN6Tf-X8>@}%IWZ<eK'
    'W|;fvU0NkK@Ir-emvC1mI$4r)m01OWzSLl_-<S0@Zho3`R<jDHqIgavVnLQ6a?|nNBPEKlD(<c2;z?JZtgeSJ+W`yk%ZKM>_*9)^'
    'QYe|#Qv<Qz?{?Sx_fcIn@)#8~bVAi_e~(2dYy)fsmn+4A?nIMRZ)&4ajm)8$MHM?=Tg$H0-RK)XyS~tp@SF6Fe0yPLNfe4@1w9l<'
    't<lGKA=02exd(8=J~T90?`swMK<VFV>xrg<2#|XQa^7@sIm<n!R6|EKq-3vOfB)-0v?tc<*B6CSi)d?TU|KJ;c}a{c%Yae6Kjnx<'
    '%36bzMFk#R#R$KCja;*ZhPHT|L!2~xFp84`_eUxJ(0yf*-;hcWedbWn1A8*B)oat_uD&R6I*NqxjQ&!QoK>kLS%=e0V9%8a2EHhC'
    'KRp_0%I+%gszT)=JcLXv2q3#x*R?T9Ag`J!nX+>*2cT>~B6v}VD4XOL>EfcGs0B$?LMLbhL7^OQBQWzYjGcUPifXNrJL<vH_^eM4'
    '={9dlibVl`l{Vu;pYzngv@vGvO{T_-Ngx(ktqC)<p_mz1`2y2VYQu|kvC7ifZJ+UVX3a$}Nd{OJP9jHW2(O@geyfs3!t0i=51QCD'
    'X1Rj~I_R=SOx|o{aPAPNVppNSrl1uh?R$zIr%@}*NFLhh0uT?q7ivD_&6btYJ7_nXO2_Y!3@MrKQE|5)pT1PF{7sC072`q0_E%9b'
    'Oj!Rfhj@WJJ_D$xtsh0>U>FIEA@WSvNEcr=rllB0(o%e*GDti-{^g189m6tkKn4!kG3@T(Ir$tZq9fkO3f#Tf5v5Q8@Yu*Rpr*7;'
    'YOY*_IV91-h!14FN@tc_CO2zhiSoq)r4BXmc=i<Q(C~OF759OEPFi}S)IqKR##cjKR4xGlFwvPT|N7u7txbAAxkQ?&OLRl6+{ZDK'
    'c{&Vro(mh0gMq1u!t=?_4K$Wd>T947$eIZQ5w9*xJ4@e8v>4tvLw@59w$0i^EG62%MXC*i(>D|IiPFZJWi{$O<U&w0a=D(*F^I32'
    '<d;^dH@OCaw<^mU17K*E9cSzc%)YRN$`U{o91I0axJlBf_QavW;Z_KKh8+DXpgs8RICAYNg%9uL`c_)|2v^6L_i%i-J>}zs?oe1O'
    '*^e#d%bh5h@EG1S8{WR}5ie#Kcv!6+Ufj+o2q)-@bv`2^1f%6$cRrgN#(eby8Njsugg6E|Qh{KN65N&qO`}%!(TC0#81{gWk|cxD'
    '=M@|Lw+1sHeSwte!GOYO299UoftQH8s-uwx$QyJ556dO-#~VD!qb}qzpEmZ?%qZ3%^OlY)OzaRTqqQ{}mA(T8kGx-y<tikLsxo0~'
    '+XdvQ-E`W{&c%&y0{=8x9CNya)38R$o(x4|nyZs;&mD#xF;M!l%Wyr6>RX3_nD`!vapz^xT`&~2+0N>ALQl0(#I#1!E9FB;zFR%l'
    'rqpxYRKH{`kBqq$VL^PT5z;m?e?{ww*^lH(#N9CkayK|-ZiV2@$gJ)ex;10RV4K@KdL~p10_SL)DK{$=vtXb-6bV^t&bn6qxoSM>'
    '@$*)^I$speT=Q&Ypdw8=V$@)htysGc?Iz5Nuka}R6t}AKT_>699yk#L{4FBaH%(B-o+He=h#L&<MbrfotM{a*C8k(P@bkdi^Ip=&'
    'uRiTj9dtq?zNq1t4;B5y`II%FTGy40i<xv|;bxGLY7IKwvq#4BB$7Ap+q}y0IVoie^!`)?ty1!U8Xw8H0Dn=DGF+F&U9>7&2WHkW'
    'jZKv6yN5J(y(bTPpBm%1F+}lh9c`EMtRb$l$m+CPcxB)3XXqOI{fobPuEm-RJLE?j+8lAH=6J$gFYJ)Cq-%~KBu4#UyXZt3W)OFR'
    'L@sK&!7jQJjwG<5By-X5MxGcoqUGYv)3GO<O>F|WWBiFo6eW(mn5DHL86HhgZ4Oi}y>@M?Sm&XDk1|gezA#Qznp!i6yGF8C1La`y'
    'tU4vC3((_%<L&gf^J<-z%baeFPxNYKI9?)NnkJX%jB2WsXX*R88XzM7uHXU)oRarCtzBz-w?_raUDmPJpJTykyJ-b%6`Txt>^*F-'
    's?5a5sq#qJ>*rw%5VKm}$RH*04AyvDDDiJB$)LxHY?GX^F*jpyFHcBPkxtP^krHuNoy#&^!3~xFp4pdhmDT6oYgj*ruhYfcCF&MH'
    'mqJ|}Hf7E0P}@G<Hu^8gyHjyXk!{(~Dw0BOQm1dSPBe=WPD=0|F@b>HT?A7opG_INJn{nUMayHp4JMOe&kwIj-3fY33Xjo7K(Ip8'
    '(zz3;?RU*llsLdAX}ach>y2Q$UY1MMH7Ot6pbb0%vjZxS#za}rtA`oI*0v6E%n3>_Ir-&&uSv}2hOqHB*H~HGk6t937d$xQ7*GSV'
    'U(L}OikQnAcmyF+S+Xt$&+YT)_%d4Mmup9je@wB$O`dXQO0{}S>8)9II7pIT3-X>LBY_3^wkdUkI%3&kiB6t1JG1G)YzY!Xj2-#n'
    '>EoY&eUYS9@(x7=@ZTqAr!OA9cy|2wgro1UGD#VEvaA~^1L`st$qy$dPxMG(Fh8X$6tKbcxFYoF*rk!eaFxw+^MZioAk|?;I(*h4'
    'shRS`>8g2molmdfA%hvwX)$%xsfbY$QRCmuN8^LEoLUibc8_8QG)NvA_oAT85<5oO_k26@%zF!e@J+IJ8s~<wS|Lwk#C>nhra@j<'
    'wnj`>%p=C&j4fk?{E}v>tiye-t&YzrOB0l9hDim?fEf?Rz+vC-$O@4hr8?gnYP?4=2B~W(N4e5Q7}zn^l$;Ipr9NpsMS*6QQe?}-'
    'th<U+Gjnl#ENngPvI48Fy-^pL!z}8#g;%#0`I$SE2ysE2L8ZK8^yE}rg4R1+uLScffMW3Az?>9b7I5IdUj2$G(!E6B&UcXu{P8I!'
    'GB@@p!do6?+!GsD!}`oSo8fyRQ39p!M&9x!8mumoo3YUuDa<@A#>SUHSBJ<DB^%)yo&U&U^*LvSYU^Cr4Wh6RA-2=@{o><;fR)zj'
    '0p0MN4v+K2aTZlW>I~7B>sH~i!YjNb==*#5{rq;^-Mr4kUvh$MY;o=^LnOooY+kTjMz5-TUB!Ojv@Tp0M%2dlG2V9SW!%Aa>2g39'
    'JP$|P&`Ua&mYGq6GM0@ERfMjj-(f*0U?(vA<Z@@i*K}jT0NNrJ^0^^NJ$m1xKI5(_21=7N3Jk+=bAelL^1uQJ+kZ|LBSw3LOPpY^'
    'MxZNIf@bgY1w2Gx7p_UjmKMrJkE|-{L1et`%wmXMZ9C2!Ps5(mN5o-)L|qa=9EH;62);RohCT0YW4Mt0wq`zwkD&x{IPPj8k3Wb<'
    '(U6-MC1wd{^VRK=ecXD&->ti$cQ2lYew*-H2lrjOMk+KjZDTppy_ZJw^Pu73@xXs_?69lIu&Pb{BlpkTdZ<0~FG4f=a4k9!Pcj24'
    'XVW<=?RIRuF>Y-1tsk!|-u;*l5=9ZCk?kzr$jS(`Lnnf9>&8&WdjlIk+{oBMVy~Bm&z$NvN^6_j{|`G)e+1E&1ixYZ#XVpTs3QNd'
    'kUq_{|E_dDc1k}_PS{%gVDRX0@HIZ#$_2a+`JH7BaHSu7)9Y+XCZ`yKVO3q{OSnWNI5s#>NfXU@pCqSzi@=Zm&AR3YEEY7b`E;?S'
    '2KZL(NpNhQRh0d5shD=^00!4rw*ia4YIL+D<5AMUxVaUWgFzDX?DX-^n2PmiEBfWTX1L_+2TJPdIe%<P7`*cxJ=<6Z51=nOoTD>G'
    'sj_wckizMZ_~RpgfQ`mxjY)zl&E(5OJOqUlJ-_S_TNjg;rM=`5mC-$YP@8R72!?CGqFP_}k`%D_(lwYCLtxh#v;okPB>Zqh3|=o('
    '%d;hn&f%nFEjeH~FJCm<fXUwLBq@MKB58d@5~b2a#che4AgyG1gIl{^vLgwGA$o{*lL?y_uPT!$B}|N>czm9B7;6z@#EBX9BJ<J#'
    'YF&O@$M>-!Ne|g^l(FbV-VsrnWGgK8mX4y<5h{sc2H{>r8LHWvqOX`ag?jyP0%*U5tL#i7dta|oOZ!8}F|(;rVys-x2>@w&7!*IQ'
    'OnKKRqr7F4HZq%b43>auqEOe3v!+xZ-zJYf1sB}wdb?;tTi?F|+;CG+$@r$dJn;y&+5}_h?B0I&{qT;9I9Rr_jsX_-*LMT0G|MsA'
    'bTVutM@yx;G4PH=UfU3A>)1PBk{iAbLn;XqTS-=90{ZGmL^1IN^{(Nw8_>=%glZwnK82<Gq%rcfvO8724mfyzx55=tU88wDn)N;;'
    'ABA^t<-lVWedREbD8+_j3AaOA8zh^`#bnZ+Gh5F;k~v#aGYi0oKW%Afl45B9%g1EH$o57AjXI{cK^yY#<)Mg~StE5NvB2J}cbk~s'
    'gCxu^V%Xuic0`U{{1!-;K$c5MC|vUcnfgN66MQx@V?S!XE&}de%-6AGFn-KBGB9>M7E$%&3b-2dAZnZrK&&M3uGU%XNx*fYn9w=1'
    'a>GM*CrDk*7eFuaoHyreWdDrR6P=IbK*E|Kx{YG@uLLX(^vL_|weSTpgtQMvv_fHocp2@Mh`{7hTc7Vrz#`^puCH+5jnZ?ef>2(@'
    'vpzN0$2Slg_IJ}3dGfg1kcSS1*u}u@zaU~6A)9aC?u7+Yj`;EDVD9Q_%XZCH3j1~kircNBM%rCRu^Xz1{S3XD*O1eueF6qR)9|T6'
    '%h&|~x4*7+U)AJE=IC&6&NT#cisHg6qG18GBdx$jlBXu7<;4?6LZVj5_7pYy!zPba3&b3?8?LNHXbe`-8qRRC`J9uD1mkh-HgI&&'
    '?t0p;B|b6N&QW9tp=YxF?P`Fxuz+yG1P7sl1KWpD!%TY(1AKSQR&8E#4y8SE=0UfWKuDKlpft%facZ=2iNNT#XrQC3=S=7G<iv>|'
    'J}qx<a^h7hApEoSG}CT-#%(sSO@I+s1{fL|M&Oag4GB8WE>NCys|`4M=(9_acz{6X3ks6Jp1bcdlDb2g1}DuS2A2I<rDVU=iD|8y'
    'IRnWFF<YSnngck=&qZH<9REeUr;u54$XqOb?`FkcAjgekn3DsJ3;OZLqqHU8MS|<g=d}Ofgf_t^Ka^m4n&pd5Xv^1?Ih^H%Abk<N'
    '>@-}SA%zfAcE`~7m%zShWpin-jGvhWoOljHjrT*(0TxeTY~YGi8oWw;6Pa?o6yiOq79{YiwD*#5upe!BMK%#R`Nh5o{D{2jX)zMA'
    'Bz@%vZlR6<NwB{59+rST&a}}^9ns~dw3t1HDLuz%HzYBoyWUvv?Y4xDA7e<K2Qp|CbAo*rYRtbD^%DvO?aD+`U-_(P$LnoG|CW)z'
    'jLYU|^DufY3ew_x9#}lKQ7}wrT}I}wUXwX1-KR`NJKoh7SbR#>_s9eRAk*RT*5-!M)W{LxuJ9Kn{fRK<!@I#SC@PeM?<T5k+qSY4'
    'YcO^&E1~TiJ_dJ_T8vM*aW>u^Ml99~1%715(h%`HymPh>f4<X|5(*~cBFN}n>1g28s6s_t-}kPJ2n~@{@T7)4PeSRB{EyIAZd4&6'
    '18t+n3mX-oDH7+Bt~~c(y55XUC$P~OY&*x>KNhQ_d=w3EcUB4Y*wr75vl^y{u$s4P#@BE$MFK^F8epgcv`MP%z<w}dP!670k+#7V'
    '-)EO`hk5l*)QNU8@+dkjvXX7#W4}k7jfgWb&gC1N$_0!1iTE_}A`NVErkC9*r1PQ_1aW0fDE^BZ;}0YB%-0JY8-^^{fk&!1lNBys'
    'Uck!{xfZzHl_)L9StTR3i(u`&s0gxI$mog^z3Algfwg#!$7c1ad-2E+S%V%sej^H5q(h*8_(;)EKYaY?)oO_2+7io^i!c&S-d1=!'
    'VOkQe@V>REt*PFziSn74wfEzALQ|zdSdG}=OB9bcz|mK8YbA`8)mkB&U1hBm0PV6BzDQfvN5%13V5p(2y-w>M&9dd9yd}1yx^7w+'
    '?KMB=V8HZF*i=`%?l!g1{_2D-I>Hau7Rj}Yf0#L!2(>n;0n%DsF-Cdm`(4U}MFEPNXt~&JB&W>9Jz({URva@ip|HGv5LCc8yNkTY'
    '_@0adDY8_@W@_Ein{t-L7btS}MF8Mb28nSGesd&Y%_(wgu>&gl+jUwIrcxMOy&*=0>_=asZ9!8g$9y9<L7SCw^1!*_Yz5_DAjxOI'
    'SMzwuqDl&rl+wg$du||)H){PN!7B@s$MstsUP5Qia#jj^aRWQdowW6imP`85A^!F}{0+V~D!*b!z|FH54HFz{pWP^0fm~k8=EW^F'
    '5K9pxlzJc0gC4}RpG8b#sx=ewl3+o4&Gm>{@fCVXLw%90Uct`75;Ql8PqLvwH~yL8PR785)&14$Hl~!4==j}8o;yDgiFfXu8!HwB'
    'HfZ7BP%V*TeI?h9Zh||fb5aKiFPuQStwn^a_mMl$sPEWPQ?|9XOm^C&GK*kHM0e&Pz_vQH*jc@cGR^DWh^u<Z-PCBIlsT$S+f}93'
    'G|U)kSdrUR<}Oepda$$HEL+rQei&*`Tuh9J)l5*Aq0H^a^w{SZD9In(jiS?T6Udk(N7T?y@$eK#8J@B^iox=xx)nSl5S|FvJT-Uj'
    't1oBa&P_32&8sCDG(R1pl$*e5uvL4JK{<A!{J5~aijhRcf~dn+jXbjZdAqMUn!~HWM@jN@o-9+$zC5>@N()CmV9iQm<o0EbmOaUO'
    'Nvc9L)_;c?x%7Zg&SEmJT5v^~EHJJ-W(cME`LAL!bEY7xWX6scMZ&zF4@x~XR2*Z8k!;>a5ApiCtTH9apvbx~&TO#Z#%X--joH44'
    'KRWwhHa(IOj}YhFMVfJFbf&BMClRYUfugs#_|)cxSsg<{qenjO`W&GbIYs?l>@cmJrxa{O!<`?k=j@Ve78_YA$uZ+|N<AiQ6f%b`'
    'j>aSt9CG{txN~+E^2Lo{r`j<U&N$*e;$O1XY|@(Qj3U*X0K+XFAq{wD!fu7J+=4_TEyUWSBaa=QRus3dg#8oapZ1BN7v6noXg7W8'
    'IW8Xv(;G?=K{K}R{%VO5mpxDaPsh`%II)~Bt<ka|oK!T;b@Zrx!r<hd1w_f0?=?VnEA``Bt>va&zc%WS?Gjl{a^oR4LyqxH{wWMZ'
    ';yay09a?DAXaU}gMpBH|3)FLs#91ty-^#JQ9R+CW=i6b6L2C!J-Es*P!%j=JlhJn=&S-nn@0iwA8cqYe7|$BFp!R`nqcjfM^}NFw'
    '^d8+K9sQVzWsG;AJPnxhDWrnw93EveW!^R1F2*qRhS7wh?jgQyV7P+KfyJH2B|O6dV>JmZVzHKd7ouy#ADzygN2}#Jg#0@UNYwaq'
    '4}i&P;TqFhZ&hb|TXSf{@+DhAf}>;cs**8%th-J9$ZHj&dXF~6C3iw?2gtH(*zHJI?I4tPEQI;UZm(Z6KIM_wrbfz1^Uo_8*1Y)*'
    'DRrfHpqGkdh*!5~q7@!P9Nu8Z7kI$EHa)~0;9+&CL=01QwmscrGP>|hw5y=AjYm2^>K}}oFIOK=yKRyJt)cdJxb<Xi!X01zy;)!('
    '?G>nY({_cT4$r{Aw)TsP7Nv@#inkziMuwKQaSi=A%5@6zwFQW-$y`VF_1kS|n-RdB1{DS5qo*Ec)Gk>JSF_5N?G#*G-@ja(E!g?$'
    'ZFpGafS6(!5!{X2M2y=Oy{S!jVVXk!9`r`0sC48GM4pNlz-@xg>)}hJyM@S)(!4ZE{2G!FXv?aIsL!P8ZH_zH5;y!V!a{9b64+jB'
    '%=YZ-GK4uwFX<lyG47n6j3rE}%wM|Ul_3Cz_liy&hL&YczC3R|P$a0UemiRBy23<c-3IZyWA8FnYb_VTsi5^=?eXs$VGp;wS2Wh!'
    '5dPnd+N8M+{X0M-XV3_3TBjSfi3}#5)UDg<o2{217-=j}Rm0V4tk3k->IDnkprDIHw>F2CF`MjW=-hFElJ7Ssp#6ldiN(9hv<Xr_'
    '03w+)b<pDR9uZ1xmz*4R-KJoWcd@k)gjHwsb`^6^N{#_1QoydVK4qQId9x^CGt=fu=Q|xVBm;K4&<0|>Wu&-q_RLp0;F=0&pm(cu'
    'Igtr;JILTpmgOR!nj4_n*~(TK0FOe0;f@E=vDM;kx69W|(^ffq`TC+}V)(Jl#!Z=yxy8VYoBwdiq?xYj*UN^iDjHK^RV$Lgm}_1X'
    '_dfn#%E@&$'
)
)).decode("utf-8"))

for _name, _source in _LIZS_MODULES.items():
    _lizs_load(_name, _source)

from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig
from v23.state_encoder import get as _lizs_get

_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-rlKO^;khlH^}$@Z1Nzugv1!*iwxo47(|i(iVCJq0zw1Vu8i%p?7bK{qHMIvGU_Rb2oDjkC$1TxfL_BiupVuJp9Al?AQPM=D+{_AOH5R|9JCX{_yLYpWc1?^yare{^8C4`1}9*m;e3wrO*HPx4-}6fBx(L`TVb6-~8#9zy9r~j~~AK<=da%{QlO{50CFY|1kajxnJM>@Z-nFH=&<C|G7_(kKb+o7J6qsz4PubKmPgM`_J!v`r+~Mr{8}Ve*5kJ{qYaiPxIrq|NP5O*B`okwqM^oJ%0N6`HTGJ!^fY0c>eMH;-7x`@%?vy``su%|MK#MpWj?t<<sN)_u3;2!aKme;+vXT-oN|y(X$G+oBjHQ?IOR5wiY+npC8|U_zShjH^T4Xch*Ze0^@%B;R&1eWQj|2Li4=*iO;V-zI)kl_<e29L4*9$<Hw(WeE;Krd;F+vB6}m7hd%W84vzITYno^Bj~D*y_y73AFE2*_@@F*r*~{-5V7oUi{}@<>?f;I>>0f?6n`nJV(J6-J!JF!0SBeH2(<cXRkInNwz5Drh138E1<%zdv<MU77zB@he%5eJ0!OIxg{;Q=9dx*0yxY*U$D?FPk<rc1&$l0cvJK1{e_-0<cd->GY-}Y>m^-onEQnv@TBl9TQ&OblhKYcc@ACO#a`{(~D>G0g=oOO>M-b~t2fji~JF}!?}w{I1PVH_Yk48aaA==Q=kcg-3+XQz#3AFm5vB!|B-FX7)B^7Tj#&GvpXw?y>dj2%xw@XGx1xa@>n+>NIQi5>*<46%T`b>EA>l0Oe;Cu@7umITm=bIDG=2xT{GmiPO)L^HMnH)dOX^NJX>d1IWuq_HtfN3waw;)Tcr$XmOgA7uMX<zG<U4A8n4Y49x!89infN3;6-y;#Eddgz;6)~_y>JRcVazuraOLKgS=r#-eFstee!Rez&zKfHhc`0dYsySP5x%4)(*Ki5(10^ilm{qI5X);tAY!wD3wE4?tI(BgiS4WBRDrig9K#wO>76T(%t9js4WZq(<W#F9LYpXN*^cJe(}U-#WM1@*U7Nvb{fD07a*i;cX|*#lm>^3&RqD>-VQK<RO+uxQ_K(sE};-zE~HLqi2z!qx9hB{>Us6{rSgxsULf)C*)vA*3RUj1=Ow*8Jk9jG!46kV#nA<j0zdBQvi@cg^-t<ac&q=M?(FzG8?xWxFq}#ajLM7R??o=-s${X>VoSP_D-rtORe2@!iJ{KY0a55QB%a{<a&v^59B-20gRor~SML?2Al|J{1T%z>3SW$R0f2l6?qXxcXV1s)~!C@qq1czFjWr9Ih)Uig>doswv!$%I+D3D`njn)qF<$v5)bcF^W0tx&{KTh^pOC8sJUAtKenXaLjsD=(9un7J~@M(3tj<Q#i;xZ)3l!UHGhlU(p>NECg)*`X4W%0omCve(aUaT!VY_qS&%osUhIBm%C}BZ!w+QE9iQ`v<mIqRD=jzvf%rp{5R}Lg$>u}@F5&6S_w~_i!quaH<qe(^skmQm<XSMJCSza8SnM|hYz0~Gpz;O9z+&he`CWUx$4h0;||w;r0mwOGMRTk;ERmfCOID?^DDtdROp+8_K6(xC2E!}-wW;EwX?Td#XH;UeCwWnQ?XtM!V+ycUF_pbJDvUS1pi@~1P?E8P@9KDd35VpurJQ+pgryn?>_!l#qFEVC_T$FqV3xctI!l~`KtQVBrf<V7qV9Q%0zt0gHZmcJ448b3&dF*Y?8=rqM_u41@S{&@51vVpw}DiT@knW;I?zcX}#?cmgHjXPEX4o@mL(1&Jjd8JVY0XHa<=e<r5tkIK-bjpKK)3@Us;zANRbS#RMtwn6vhn!t%mrJU`fZbHj)2_k>g54UCYw=ryehk$Apnr4yy+=dX#v-#dH=zpv@nZM7_Zhlkh(Jau`ygykALB(qUa$5I|e_<&<0iANiXw*YZ1p$*p(==}AWjLO0jEhC+iv9n)nwpP3)QaH0ivaXAZfbW|e3P||glh}*R%nFOB9qZXPz#ZaEdd>G7VsrRDND!CN&M{oYLi16#tLK}A;S1@>(c<F3+=mfFsy;#P2$KD7aGR^u*{tJk-x1fUa1mjX&F}UtEuIKg(3b5ggFNMX|I^PO-#z{5@#Dw8ro1?UOJ6)#xLqoBw&8alTV^TIRI+{|vv>lda6>9$7PrPKf>Wy<(E=LGVBHDstLJG!Q}!uP^q3nmXe>?@nTwrkW?&bio7(o<$2?=7$TB>gv8ns4M;X^$YR!DuLOjr5eiY#|&~PsDM9D`<?1aX_)Ko*t9+32_L|v;Cb0g3t${%v=5UdE2%yq9yYZ?x<a>>PPeEo;js~fd<;fY@(Et@vTp$?=4eH!}O=0yP?SB$L=;bMIz#YfqMhgs-aF^#q`$>aknp2B#tn_mj|WN%+R)lt=RFn->>44Y`?j`vzmoudRiE!EBQE#6e!WQZzOa`bT7-Kvn8FU|32I4sB^!UiSjPM5$gAZ@3$-_!-l%qva_Q{-f{^b<U+D3y;?tERH2AyrFM;DNJ%wBVqA|FKiO8HOX#hUeU{!FoL{tc`k^upSuCO6NrT;t(9hsdv#0zV4MZOr5eBQR&%?I-UW;gFi-7+MxAe;(<)-Q_5(YW(hIig`UF?m|$z5!N_w<%emrt{3o-9t|CW!r=hDj9}cm?dV;dUxXH379Bz&jM^G&hRp1@udyc2>a4%MDg_yd8EZ29@#hq#4XxGKKS7XM48AHhW16!Nx%J$c_*?KcApy6>;jtcN_ctsfPPM<Q(kvWRCG>f66`FtaU{v73e#uSq9U`5&es_~g($rQ$1_HMl^yy<>Zqf-5JDyfvJ^Qha9@=#4eHq^$6nDeR$MRq8UjGHRg@Cl>5A%{@47x&(++AgnrxrNuZ>Zw?mh9xW1L{&zdje1C1p-`*21&V8Bpg_KOMJAjpD}SWr5a6Yn3o2dkHb?s}Lee)^)($(7des%GLls2pbvt+to-EDJ6aHpMIEG2Jo)@a(OYQ-ai;n)uQZblVePhSDfN^$uMfD6lNQzUBy$*{Fy>=WrjIYgL+Ewu5_cr8CPpfb6^wH=WuDuIkz8b2wqanYr^$ILwbh3=nC^{roQ$m9z-g*RGz+<Ag(gyOr0!X`xzJxeMvt4-iEA5vYk>mSX9}&gGuj2`Q$(9=pxX;1682a2^RmQGtb|?-vgZ4H+=7$gOulCFDe*3#O#nd!Ihq|3Hs0b}Y3Tq(^b6x)NsLeZX+tgQo?0J2L(lRwPC?fq?_lZ#1G&jmB4p-LX-9r|Hu~`Lyta`4i_L5m$wX#Tt-kzT=;Gad6-!XVzrgpd`DNgHLoaPL-<1)~<-j`{63iT!s2;s`Batu1Ow>Mc6Mdy~Vl9&zj$ve-Nix_M>80jwdsaGaf#+6#c5qu{)39nw+H{o@Mo3vCQfJ-2TrI>PQSm*Kk?=!+%lxhS0{WcPQuM|8{)SJoZ1ppd;)_^P)LB%#T$_bF)>WILRYGF_v!s%6s(`Q31s#KZt*7IM&F5qo1$T1p36#^qn;DBZd{k!J*nGZQdJbzzOOAqF26xk}7dsBwR-M)2Tv8ml|*b{8_6@WBrI`O%Qq|6<+Xt|nXcv#~#`j)sHj7NKcNnz7D>qO{?ie})M#I0+Z>9N2&qsqz3IrF>z(r{KYJnmv7+>ma^;8+B@<6-ztuu<F~@e?l$6&+$oe@0`3ZXnpk#hb!>!sY|mNY4aOW)~|8ygF4gH@Z)_o*&NW+FeNyE1l+*Zf^%)wDhpMXWHo3_&*#@ZUzO)7enRm(JI1A>zK~@+@haQG4tZs;!tu^xVX6u<KnCaeo0!K%v^;J6NEb(cq1>IEMJ5%w`G?m2B(C%{o4vUaMTpC7}QW{P9?f0_mw{rJc$8fc1A>1J%I30c=OwR-6+u1wpEGBx^@6kyOF@W9GPqrlijRyKZeQUvNI{*zbzX~Su%zGBJvYHrV@xIhFu8Z-I6ciJ804QO0Hw|bhtP;W)*lsQ$DhoTf-f_l*|R9e)mN{(!~FiXK4oC{cW7$>sZqJ)H-{9l_Ut7&(I!f4WJ9WB<IQE{W`t52Kd~ClFoB|Z7lKgcofQKxEK3n5f!Ve-#?m9TQq`nu5+StjXC`hgZ(%iPH!Q-#eGQB@LU4Tu*wx3jDfOHEyV9uQ&Izg3~A#$gwG13eifsO)Cj{&yTT_keB(gM8vAf?%kWY!;hYQh+~h`&8eJ858FXzTl`UC7m;3!dKcJ!Q9Xv^Mc+cR5mEn8N#yxK&l0zdy>Np{hCj&!AQM1HEj2T7q%w)O$s=_Uu=QD$~Ayj5X^`@BAZm_&=2%~Nayr9O&BSmLFS4<*lGp$$6Be^*YZ}Bpq-5j6Ijzs8?za^Ps24^?O<Pj<XM#_Ct_`u0y_v>xjn43*r7{ZzAV?(6hm|tVgvpK=qw>fDQ2>v7WMZCHkPVZNkllkeSod$=*mCS7g{o~ZB9=q!ZPv1JLFwavqH9W`b5f2eb4r2rsW)Fm<lFU7&c~YXco>pl+h*L`vACa)+fBy0PKl|mVWXp4?Zg~bPxNLHRV@98-T6<*gd@=MxG<U_<s5+gLo`!*dWEAdlJGPE{DFDJR)^(zTU~U6LKTed5@>84|$fE>gLmji3`jAzb9m7DB#N=DdRMyO^b#Pm^<bpQeQnmMF;3bEyD#8w}DhLO;r2RG}dZwLMI(r3y8rZCk*6Q`qrg95cTO-*dXi+L4BTy)bfET9~dzjeX40!e6wt|q8GF;JI(k(;RB1ZezqPHqFqct$qcnnjdmx%a~xF3c>4J3NO#%KiQ8;#iE;lX|a9Uox}6euPiT4uCfCWo{Voe(Jd8^)jN)1_!t15DbH@Ci%;w*{Ajs#(}M|6D$t-++8v{R8IU*X{q3(>|NKm%~NZ6LCUFYO#Z(GP-cGft}HwCyw9vOCbY`XB%}W5qYp_32Qf$yEVOB6!OJ3#h|r#SC3ibvZBM7u;2$f6HqC`-DX9PG$zIzAyysYcR)MFX+d^)7C&2qA{<x`ji?F+RJLLd;E!e~3}x1m06);-`-iBzuKw7=t@*p6^$ek2jGPy2!!Rn4XKJ5$MedczCoTq!jck!Ja~abB0VHZphWjDIT{Oq$G#to+NULw{7MDyFIwo(UG?s0jw-cM7C#~f*p_$#0C@6eeA&(yk!zhmh51}1<c`$<=o1v1b0EVs%O6r%1ypWiUSj&}MXuzwj6)t<58#G<-g*^p<WdN3?u=@;<J63@8eNfu4WXx;+d2u+HfP7IUOc;()UBHH-Pomii^vL|);Sw!*lEG*kwlb0oNK#rxh>_;XC}Az~S+a;&B#wzlP}fc<5~ft)^<*o^W%sLELlIwFpJryHV*pb-1r1s+#)Z6=VHr}$VROvl9y><8)dQh%IUl+2KYaM~7${t`>b&3FXdMBKQc;th9fq?Q^C;TE$N><9g`R~Z$vPF{D5QV_WmsuCv=Y$}&&kjlqf8Q~k<13!h?U1g8@B3#!<xGW7bPYIQ&?%(+NAYh!sEn9VsuZjG&bUVb`*kA_jKE{tp=ZlgbSJkM~$74lD;K+UqK!zv_SZ_xVfH+YpRo2)J~5}Ljy2JTGTC?!gxnefArsVifXOje$n<C$;|kPif_X5ww}m{W&i{IF_$2kP@nQRsK74Dk5w_uFzh<b5E53^J00CR8Y15e<!TXVII^&J&Bo`t(M1L6@sr9=$D%WFAooy^{mfy3(d%7ey{@Ya#OPh1Y5dNztLPHo=o%w+O#=@hPb}h%!^mF=UbG>P9Fp~_L!9sQyrs@nhU<s-(Ji)39|PM@+f&ySlNVCtML=1<d^T&?rBSXNCXl#*ERhc(`WdeDWTLjeSVt~leSvw8+5Ya!f4FJwq7y6F6n1nmd7fX$&yPF3Jdx|vW?=)rjP|HV!PC|bLtUOol^p{;^^dMOLYVDx!R4sf^vkPLN#&X56mWKe-OS9!=fC75qfT7$-#`=0_9#!>@`>&Ux`{m@*F(^vcq=CRZ>O_0>$V(37AKHbm9<1ps>)={MbJ(J!#|dqg0?S*QSX+o>Y+A$?a7<#tw%k95DcaPJLXU%-R2g9=oU;_dp5^uM_ug#xT!GiljAp{auk{Cxz(1fsqA`7e*59tshc%JZQ{tPw2E#nXB|oKFkm?UP$SZx>&!*&(3k`R+62svthu^wQhSs2yCRH4&{}>O-~XwqlB|b?_*Ipw{VEwUgMmgeduV0e)bqHmBA6U|WxJM*YnE`|g+d-BIW7sfXf5oJho9`YL}Q;Nsutr2WF@fvXN-6d3?u>H_^ZB)|GTude|?<`XwoT&_$Yr$mKc#BGfw~4J_Z%aG^tb2dbNA>Xlw#YknS=Nn?+!krMHjKikC)@0nLW3Wr~9=$$EK6hTXuE-nPA$q$29M7T2f4YQ4T8&^1RVL#!6-i9l($zooY8dIB<t-$Sn+{(QeZd|H;YUT2ehxjwVvxQ2s#EQc`~*HKwn!|H-iP0+wkehErQhft?USqw?g=DMLq2_j{AlVK{LL*fxAM+lP<$`l3AsM`AA^mf|hklTw_j6(+nsT6LFDJpz=nv^XYAfaTdxls^0i+)UL*5+_YJuFk``&iSTN{Bwf^+1Yfa989+sS?zGtpDeWM)0zthhsJ?;_K~G!y^^cULu1yvWUz@#wyU(*N|i^Im+9EfOW_r1E;83@RQn-GUckJ94$?rEE&Hw%NJ_(prDI!Tuy*Gho%b~h)xI`nm;bw3uL;*rikqCR^s!0aOi>)pBfQ|I3v`~bk+u@i}3QXCp8APvgdrqHmP5Bjg0UGSij)yv|E3n({X~ggAspPz)MCqMwxSS#-ajYQ-l*xo+0$xhIAJZ0pxzStW*|pnH2+j4O$bEo8ayqj(c0DoY!%4$J0B-xSp{Ps5Z_<uLL3y#5i`Ug8{j3<j_J>@>^v%N0_eA$I?ij8`m)$Z_wk^N10OrA&>nh)OZI9H7Rq|K3A<A+mZrl$KAcSG`Er6t<De0az4kf2GmvI=_)e1XbaNY5JqCB-@nb0EWf4c)&g8a;s`w@2SZJ1a-6V~X(zM*vMF*K9y>qnp@aZM0;K@1l&tq<u=9DOcJXC0lvk-kJ|L&Qgj%FuZ8KCFKa29U>itjysqBs>U$6VY=Hb+dWI~#G(J5xXY^f+E1?K~4F%P{ik@HF2&|uoWWO^?N^}b;UHMqn<?b$UnY6$3bwAP>^<6tt(!bh}^$%&;Q$(3nHBYhJp8<S2X1yaF#FON2Is5)AJ9!mhbGbEe5nl7!mvxN9M*~jqpwecMzOmV3iiS4eDH_iC?uzrkZwb<aV-!Qk}9YT{N>pF9zy3`z_VS{K%<=Qv|F{M|J$vQlgHJ(;lkiN;6XWjNX1Ax-VR+rfOqILTS+?)anAjE{sinU^#M-;TqZHmhB931HY^C(mvG;A`5$`)wEzAKl4d&8u)V?<rm0F(ti{z0u2_?ROyPeDm>p3JCokH&GVPWZx~{!N&FH$*5phc%}Rzv2{j(Z*cuXygvjv}<c4n`v6;aeXl;#+cCHQ5`82lDDm5Zer-Kct(j0(+$pPv0~7r3D#w>_NR#*o_xbwuA4MRgwq+h=qj40!eH#kN&JGsGMge=m^OmURgyzilZx9@g(SF*g7!G9IM`==%U^UNDraPqA?sX45P0S&L!Kirnm9xT_Zt$mfl5p~+**R(jN(_xN#Rkvof8|3js7I3e=X*Z#=#-p%QCsEMm8dVP*xMz(?&XA<kqY8W1K8WLod-7nV0Ot94)XPOUI3&N@N7t<f6E7+?-b+T5{u>`oiR4d;~KLhv0liAE#FvVx-w&&YbXovde%l@?y3X4@XO@DB5MXOF5^2_bo1m8@z5(f%_rnl+u}A1Iym&;}W#T8sRr5`@Osn4xF26(^l}?lRZJ3WkswxFsOR@;}2?-i+j2`rIU24TnGfXN-Lb4SxFs}Lv>W+df~hsLOcwPl%CcYI`)FYEU%IqVBV1%AOMV+Irq;-1UZrWj8VG_ih9)8Ng$0dLhG{waCnWlU}|YQa8bTwUMW%Ma5km_F-!@A0D?a(;OvtQmMzg#H~j^WG^T{{W|a<sPBUStqooC93f-qRO)Nqnd7U{hEH&P|$fnPvW4we->l6l+LJVLzi%zF0t!)E#rB%8hy%_`RLj$u&J~H^HpIkJY1f3wv-f>m@szR0Eeyy94R_2oYCM)5aW%4DcdJ303(DP4DRaBh>)|g?64|r&+onz$Kplf@LS9crViI$SdoKUme^^`=qIFi7mkPy#J&;P32Fx~lv(_pqS7)&3cWp$1Sfy|MSl`+m$ig4ywJ@LQIRzCgw@!iv(9zTBkYoj_gRIQ;%LHJt&K(+e_@u-dvC(t`rHjnOkd7R3p`yn?nAFt#p7JmHLZ!o!OMoCH&jRo|RT9c-*5z=27n-k`GW6f_fUpqF#sKQF|8N^&k`8>)hBTPJX=Ld*4(2s$23k*(=UhO{^K*0NsaZICyyl^2Bdj{Dg9m5IE`vTnI7G#Z!PSK3i1nlZ*sdXUM&8Ci=LoMttQ?8!m<A{&)T>Y`Nn}{|yYvVkrdJzb~y`$WU&&=T?M4{1hqu0^3a@6SU$lb=$(MTVK9R1j-lHuS3@7Cj1;gvU3<%F@#E+hh7V3r^TWnx!4hjBq>e&-a7AvOz%6$Sg9E9l&_)lVz^R^tOi7*V7E($_cTk|KEmy`Q+YIdX=iLZHtw#;vR%dDrL)k!bm|Q;|8V$g4Y3vyAtPMd``X;>0nTG57$}9X_|MMvO9c5Xxi@Tfl;1vfjm<MV6>xpP*5(K4Y_e!_lgQ%oZ^`sOOsye)w$3SUSE)b10zH#Lr2x$G*g6Mj+Pnp`9%UO-xfZP88l7tj*?<H-SrrIT<j#O&+>b507X`pjrbrC~sxN;3P{!HzPCBlAbH|eTJP#;!MaMBTcdBFU@m_<{(3mFSCW^2kp{`SS0W3Bxq<-j4(?Slh!grJw}-bMBNOX8DyQ+a3B#nSF|`85WzIrGPFxIkRUF}tH6NM9~#?d&?Rx52U24;<`;Vnj5ZC%jdt~Fa$+0P2?iC7gd5UwNvNNt>3(I{W=e<#oJpWj?x~;|?G=tgzif1!)-|>fw}lA{0V630a3&R~KQCz_5Z-*zs6sL<Eq(}Q+&KQMBXejrjejqTI|s}gycxoY^%4Z&7>74XxaJ12!G+=oPH-Vr2_5&t1{%>JT<ECsF06P!bT5w_H2j~L<usDO3A!u}A4l{QaI!`!NFrl7m5CdapZofcDRoFtYza8MIx(W5nCLzCs+yikvk)QKwHPHOuITsyXAQ$1TF@|;^C4bPc+kRcA_9tXTIjJXOgb$+X#J0+rKRQ(6lKc}lYSGuZ8|$oG~b~*$KU<<z0>x0Xy5Wv_DdgpM!0mrZ=H-*s=;Bv6P1X-kR!<)B0%qiKAT_F{j;HyLg*QJwvV$^VnJn4$lF;l?oL;YkoKIN6~m%2_R$ko#7Mt3*J0>hqCwlz<6hc-WzJ@Vld<saumlqNX@^V|Vsc*YyQq22KV4{8WXbYOXbNUj3Q2KAIodjgSzWg?ENGfWxhj|LgjRalC}zBIU1K#cE>OV%WhaPt4ty?(S6cOG;Q3r<L}uPorxt~xUgOYMEd@y>DnoB`5N+zkzz0FbG1)gV=uwtn3zZWT<z=8K6(*h3F-mp;Ji%MF9>7Zba3}kHeiSC59nW=^;I;0j884f3YUjIBIwOjL%os?=k6|cWp3Tgz0Nc1^m;<h{`<-Ow7G1_6K*kh@(k*exq!6Q0thy*fW_BH|8L{XW|K=ph>!FFBwN$H#jHQQFFe8dQ9ZM;TTG0<qmJf*mN|)$pJ=JCPuLwAM-P7u5+Bph1F`o$*g6uIj36+wgcdFP)w@SWRDt1;++^6BEa33seQb=Jay{Qg@Vjs^aidtpO#AfwI0_^IaMB+^jS>{wYeT$u5iZk^+x0RYQ1fx-cGbLSM>-(!(Fns>>g);GRI%GsZJ<8;Jawywn5hrE7scaGFw)A7p&oiLj4lK6XXU<le<K)T`0eZzT3=5s~eszc|0SQT(Ko2Vj2Ijlyufb!EJXzPz8SI&?k;7l6?Z3!$y;VdRbr6@e(9z4TqMQC2KwY@Y<+oZHDXKKm#oE2Q-EGU=W>iBM=M|BJHwCXZOCRHU(Yi>lxs#4#mN;viRZpO^zWk{9bbzhl{%bB>XdW=mA`;cd!If;E?<yL9EEQ}e$+68{*6zidQP?X&2R*3@RZyqT>8ORUl~={!^4NY-0Wd>lRST@ti%&C}IaEJ`4sPmPLDC}4o!~Mz^@y?%s9#I90&8e(xGpy$e{OYiH&~&sg_Nm+$!AAWrlUe};-H+`q`sP%dP1yA!a;0bxrri6s0oinO!#>@SX<*F11V$LTa*XMpZnGYxKmQP0r44z;@}x;stgp3((QFFq7T#A15SFA8E6G;8SyfxuuVyYF0)I!W*AXD=@49LDCzoz)pU5)LW(kGA&+oiM%Hf+X`l5X&!XdT8Fn=MBpu0vO*@sq3WD_uQp8!%v~@fWxf|t7TIhjUH>oAGlOuI4s2GQv%vH)VVPaP!%Of(1jOmI_&)FJ(vAd&d+fyiNbR%&I#Xe{N(VuVgE_~hddz|RyILT3<fawTLgMuz5D}-<dLv4E$Yf_pwcnaw3O}FZOLm5lzX%V^I5bdD@cl8KBRoZsUN>j&{kL~HPtlVPy+DL_CL~iiZsY^{x&e-O`95MsGK<JX0>JN=Dz+$Gq93)NnLP(lU%5KpqU&w%zThk#*jkvS{bD!8Dpim`gPSFOd^{cGQMULLyt0o8tjGqYXu3p|9na1m+dpX_XrDJ3+?nZwM4R{!ULZ7Oy8Jkp2YB0qXd+4!Pgt5|RRbiBf_V`kYbRo1_mFZ5Yqm0r_VL@qay2HQy2?DdW**?F{W;+TJ?5UfiV5lw%O6e_kz=xsJaL=&;OIw&1Ge*}Qy{Q8UtasS+ddaMi3_Vc>R-tWSi5}Ksyzt=}t`b5A+`!t`%`J(lu;?0xR;K7JHr;&&2_@-4L%!-N$J5!tq0L`jMc4MSSL9U!5}NN2BQ)PLMrhWH)dLE`4{#&Z@FKzHzboq%Eg2c(1BU6{k4#k{iy?rSuzR!SxFwEvLsOn%#6+LoR!&pLkP!W*0t^u&b}^Y4{22<P1=b`wH#t)1NwJoJ5V%NP=Lju-9)O5mV+Aw<DvI()Pt}d#Rt<yr5%T0*OPFD3DVjENn0APSqFMJ>yR7WE^W4{Ngaha%k4_!wO&o&S>4Mf6ccmFvZbmbJA`VQq%i9V#J~2cX!!u)TrO$hyq>iK6nwq4nvjFu*g2kR=V@#Ob?(!Mhy^2cOH7@mMoB_?owRKsy=`JSGOYX9u%94SD6Iyu&%LE>h>38IYyYPP^wLtvxBK-#|ehi`-FcVJ&;o$vp=}i?Wwb$7rJy<f4?r~j@;kdM6wCT=Sjby3_CR8WXL14uS|9BD&f+Z@N$#qd`cr}m|R=s)(xV9(2*CEeRP^^883eCMp%`~wOC^#bfA9!`yDdUSSE7G*c(%nOIy`=L9>$R8F5eo(u;4Sb!aYwu!++8}e0Ym$NA~dEj%QeR3Tpwl)t%!Q;_teLSIP~>`nB*(T%otKz@*%vFDX(_%mn`ZOJ}?<oHvoO?cB1YYeUze~f*ln^ZbU)`;dUaCzXXq2I!(gd3o=aAT7~skNG3(u&0(=ILuKO3H*`Kk9Gui6#KRp8fo|{7;{^7(SUMI1Uk!Zn#cIYOIm5^xKcPUCERbGCUq2VNTsRt8*as%19#oWm-9mde<e@5;+bhP84IFW^1mFTk=hYo$_KL>WIEGL1vaagUgM+h4O6d(Zlf~n-vN4EN(9lZ@;At$@$cr(KLku~BGqvxy7J{f+i74KR6C5H$*N5<s@tjbVv(y-$w5jZvtUQlIVYVC+t1}c`N0o5L<DZiT>BFja;sOlGMr*p57?NwT>Vs@N*bX~1@`6F!^jf4)!(Qg%r!U+HhcE@hde9I4@)tUeOiwwS-xL7d_(vfE_KlLEnfMphR21muAm-xVONc4Tp+g_ap$dC)VY{aY_9#iE<^YvC4s>>brFTGD%baP#+=!9hB&p0PnP4-c-BO2!PX(Xo&V`NwT`2H|m0Gs7bnlfhdo9{>4uPkeC~WeTH3OGyLHdXs#-n)u*K=^psZ-%+1^(?IRZZBGhLH<zeNU*vQ`k6dydKiCHdT~CGBK%)DRz<Pr}eyg@Gq+x$uscuD(YC@D&*pNoT!b%fCvg(5Wp2sxI!0<T#|Qox!)*@@T1~T3&jzzBuYan*i~(cn$`B|-Rsd+4Hlv@f#4dSm}sEhBHSVJyC+?lXw;D>jdZKHu5zwFzP%go&=?;LNFnc$_!!29`1%%+;WDMdGWWUIZ+j{<fEAw(6Vw^F)T}_kbzj$wxSUN$9k?Kn3@E}=LV{_(NF5~;-sR-nc+deMc=B{Hg!YMHgWalIExRB$`|T$;%NU@pYVBV$_mj~uoi|(3`&=7C6k>h4{*t%mdWtdcSf<W*k#**iV*mx<_xP_XCt)g_M)D}3p`+qT3!0o#|1(gtF`Fn^0XRZTpBa-RTu*u_WXu6maQLLQ84it!I?;>sCOBfd7)064I1|^09NU(|foEgb;IK4kkcE;Bk|o09qBCHZVI`_-O3>3rbYMK%S6mS3&BI@f`J***dAQh|rqoLmYkzW^d#j`m8~*hM&bM@p9Qq1L5Q&yu+ql4n)IdaQYpHg$6*+C6w!3-Sb#FhNtbaacssyVYXa*caRzO4y*09CA4h)oEIgp)>Qr2c<_eSOVjMsmeBZd)C@4I)o?aFk#FvxtWUnF2$7v%o;yGbF5w%54EmA!GfZwJjEA}}F&-QLCUMq=w$oFdb}^|GpP?2I}@`D3!&S@?V#U*{{`n88MvOBaRNZr^o}wR$DM5sM^*<TDX69|P=o#|_t|Q*#ybUgiZKWW<79Wg&gma*@M(A^=pEEkYXy6HmP)pboiqtPZ}Obuodt@SI7g5{h@*03186(EOTKNTK%Q5pt{?ddghQ%d30I^Hr_Ui(M$4A6*k#X&}F}!GrIe+f4VlLNBX<W3<brKY{F=-=|7&bfV=ygM$)q&(|;PrjXfTT+fuk^+2Xg8!btV#wlXdY5V>dpIO(*(yIVdL*=hxbXyqPYDD)qbAGZFQ}`M(AVn211U8|keY|z;46<+z<TO_oH`Cz7Q$v+=bgIrlG~A&<7!FQz^NO<#*NDQ0T1aTdet@ec=_kQ}CSlMXTo4rvWh0++roJ5tZ_8k$60g^(xKiEy)ZO>!8>_5KK9wpS76@i`$@ze*3h($@@F}Vb_AqdSsAf~#x(yS_PE;0B)y@DrIE+51A(765Ig{`qUO>uoN9DzOG19=07P9-Pc^q0f<8n%QPpZ=x5x)bR^5YD0>hW}Gq<gdMVD@I|1cC$baPX2BC6I!hfqz4bacfA7dX2N^v9G+hA5TK2zIUKKusC(YEw}akIcFLzpODxcMV1{Yz;3rzxl<Md@RD;7QU&Klw!}L11!VMC!rH*!x<pX%iBp9ENG_=@R7t_~S&>_IpanY5GikP8_wnM5h<?WF@`&Miz{U&9uU#-SJ9LWrv=pifc3h<W<wm-?KG<C$s^B>0fUtz;bK2!z3UW-%cd;7kfI+0$?;~!YwBWj6*qSj7cdNlu7IHh}>6Cd`?JBQil>Wo7N*2BW2rq64;z-K&Os&X`yucEV$`^TW9b3wKV}sc#o*mi8MZ1)-I#X>D1v3(k@|+v<xCf2-#ex`{{VCyYaWF$b7HTTOg<7|rH@l#mXa6on4Mo8axeO-V?S#X6FgRjU<9J7qev5q2vKW&r3MG1Ur+sJsc$tdVQS7-FjLZrYR?5o%<&r1%KOjGXK0O}kjwtkE%TA;otMw4EvMv)mESa;?gk?$}EP8Jn&}@B*6hD06Ac7WZ+LKkNzC$}sjRS^r!!wadj;oaZv}V=vP>1M+pWqUH@<;AdBP%=sXoaX9G83tLvSSp1(-5OAypJJD*hNCP*Z;=z)VkJ&(t|X9Z4S)SBh1E8LtC~CnAcSMB)aBLEC8bL5Onb4oX0sTm9cJLJ-K=SG>nnt@sKmjULaqFc>0l}CY8J5G3eZ~l|{lX4!3@iU(~_Y1#46Zwr*YEL+i+<6%V`0U)Lf=hWLSUs~LECMgC~1lbM<;aDp-Eyf$T!ZKchE1)uvUEWUp7acej+uVu~Wkk~N$1yT<3Te^{%863PQvMFOFYPE}+a5_RpW8joTX-g-UPNWmMC{Ap1Z@t2%z!PyO_>!l>{0vhd^pDmVzLc2=$sr`}AFARKFheE<SpLU>G0r@<scGJY&9A-PE?*`{XGkjC!@0xFi~oU_AWc|t)hD_~u*1dfsYg1La#Zm2@kqB>Sn{|8=HS8ytaefZ-9@YLii})1c)~O7Jy)IV!Xhn`V~J{x3!w@%d#Qb@S;WtHz5%QV-1z;Lh{cx1zIto-+z?!*;v7bbYN;mTt=3sjM#YoNW#?1%M^61FBN0=?98qEBshIPJbv}J6?bA?9TuWwG*`3yb71#=cF3ra%w5Zqyu(0Jy3}aXb=GCagpw5fg`J-#aRbp~f=9NwS3LSv-Cu-+hcqfrCr{JQ2e~7yim~sX6wcxNRnzu_|<{(xYe5D|_r^}cIyvecJl}gcEq)=U`2`Sp(>UDHUlg)0dMa?Wx34g`d?OvIFYaoV&SAj*rpXgkXb@N?Q0o>_EBm48_{`mc9fBewgCBShV&x7eQSnXh+d%N{y&EYlb5(?I!WGJ>0D>D(i5NY-FNBag(&R)RmdSwl@d#QlH9s@{ReE9Bn5qk*&H6TAvOZ3IdrYP}Nl~l_k5{A>zU4~@jTNZe%0Y)|4SrIo$2l$1EnZRZI0PqWhX>K`1G!dF~Rx|1FL{k^W%yf#jIiVl2wa=#zwQyr}aCgFgaBcAIf6jW`>Kj#QB1EB5|10N_rkkQW;?4@eJ7_m-1C((@F#zly-c+sBwsTq4CIbCyUw{`|h8BRNsn+!&1Y)&l{MU%}02wC}fx&{<r(e3zn88wxRJJicSTeOo$HQxf-we}NpcrGJaUSvn867lal5mkju!VY=GvpS;2mI;{h+WA<@JSq|Kzw#=!34B)6m>|850A&qZH|_z$Mtx5%g`H(f&*K)TX`WSha3`lPv+z>_!x8-;k-oFesPc_XwU^DF?1iwBek-(or<A7Wc-IP!YIWlY$PKi-(f>~pK!8`hb9de;^<V|3Dn1`;TWkRdx!xbRUsDtHWx~48s$brFyQ!GJGX3JKZR83{gN*%z97ZSr|>*pR5>PBjyaTcV46maCD1LVAWyXZOHq$`v|2+OxktN9jtO|}9tMx_dLt}Rk1<aA?m)}%^yWP_#$c_PX!k+%Fyp&{Xxn|I=IbZ=>&VDUWSafETxg8h-OtNncH4;bt_aRvr%S4WhCsI<2@=NDZH|C@Jym0mQ+4RW>tn~cLMbINPi=GEtV76-tNW^&53nQwTRfD#D@0`DkLc{Ji89{rG`x|?Tgjw<Dp-BwiSgHfDepWBN<S&<-7d05-a|y}g-``jupyzmo0Ug<%_`i$_t6^*IzJcTA>2_G;4w0kzRzsJRS)Q<N_dbn@X=iyfaSgNbmV^WYaY7$t3w&i{jaa4i|R}KeYr$u)Xw=QLfYccVEW|?&9PM|{oX&s$}e3DD#PbRay8v0NHy#dRuuzpbCcAw+Fjt=aK3c@fITaX!*Xl6&wo){lS;bi;U2?*ua|QtDKIp1%ub2Q5HDIR5g5t?5C5roc~w58DkOAGDs_i~{5#m3!#BlT60&H6rC%>xV0}1u!bBZ%%+`rkh9O3cY)67gRES;W!+?j(bZCOd!;xgsh@OqIGvC58C9r#XANpkS!OaO$uq<B>qdS+VWQ4W5C*BRcQxM^~jgtIW^(6#drBETWK2_s*Coh4BN)iZ%^|FQN6y<1nE_&$4SfOCqWfSV#bnI3iw?KSI1vklmO=iS13LQK75mW%ICgPE!JReC%$6x4V9zKq#WjQt=!q6E-2A(=|BM^|HE~(<2njQDNti^)%e6(L9%)6}-ux6ZMM%z!pUQNHPD#}DiL)Jk(1A){CmKUE0+{26$)65W_7S17sX$)@ZFy+@&kD#)xhwz1F#G`wh{V!KOW{Ra*DpU$c>jPkzE?Zp=2<MUdAc={6=9~Z2#F+YopfTp6Z2V$Dai8md*L>7(m9A9)g|SY!2>HXoZsjUh;-uaLMt2JN`_o5<8noty59103Xp~YSLUBIb7VPjs>j(2P<*f9gIzut|#aubkFnKXJx`nNp0s2Fki?)Mhr}%_S1M`Kh@&;W6(L*(_fhhk1?|`37yC`SA3@O{AeGX%PlOTyiGH1_3&w{_O&F7-e3eEeXObCvSXn&hwYH)BA-y%6-IF&r(ShbjA5Y1A*UPkThbj?^0IsALZ2kcR)s^!7C_Gt+YF%ZkVGe`*003jGk1fCCRYs`$W4Wo+J;_Z#r;@${o9&Qdsxpb+`oHK_z;hdR+ohM@hUhc92EQ;OE+y?UqA<GrCWZ*@xa?k{!n8V6gei@vjb3*b&%oIj>F3L<KReam<V^F}<_V6*@BEgbL`>lhPp+*1;lBmELQWzy-G!2+u)ULsLAcBtL=fIE%4}V^CNWwi@pq|Ji75$Go(sR_w*QqQpJ{@{QX|;(9LU3@$f~h~l*lQ<JNo7P?7z3>k#w3$!qck-W6+pLeuj!Z%t_7g9LiD}fCRp1I>oFCuO%2hZ5_l;(RbJt3RuJ8ObO%L~I54VK%1WpbLohlEMMN*shM(yK@kqxUV-STiYc+k_%fM4&G@m>mVUQZ3V^lJwM?WP~5}G3%e^WxSB;fDXpaa_Wo(r6gf3HGfql{Ptx(34J>|-1BDUM0V(X~sBZcA<Xku_C`xbKr*NbkWWW!U(hXxdZJx-TW1AU>oyX-MpYv?j)I(<lgNNc3&vuE=1@M4m}k)U^lD_eHrjH24M;sy0>5n&Z(PTpGYIS#(dp_X!bO2CcRuz+r#ig-Zy)Z&CO%D`P%&0oN}L3(@<gNvPbJu__8|jqCt+x@#69-a=hETD;9Wxw3US#V~^HQ*NJgGkqgu6yi5?FZe?kr&)Ar;JOS|Zpr`>fZh{!R0h~Q5?6V^{<#rV$W+yKaa4Tx*=(twRtI@32qK}qn!>ShgU4X}8Wyb;7;?B<k`f&xGUh=d`8Vs;iI%iydERwLxeRfvCp}R$jDn~fA7_G^<Tdl+PVo7*PdmlXh_Zkbgc7`x<s^y5DN9k%ozgCkb=o^I=GinzXI8t_O^s!SyyKEWOsG~Tk4@^M%Pf<Pq8lO+o3>4aJ;??Gatz2|Bl)gL4g1(6nm({8ap3Fo4FyfA+o*&n^R``UZ-!5mP$v>|yD-SR2QsRkNX0}vwYYS17~2M02}I8rzDWCQjNF6`O@!wo%EsV340-wbQj$hmX5P2EB*D~DFY}>2__}byO*4kwUKF)H!$_v$BUATO%oH}K*nm_x9B^|iu}lqXaj2Tl?NFV0DU4;w?d&Cy?&C_}%9UTQ0$R+y=1Aj*2~i7ht~){Qgm^}D$4ltZMt;Zm8muuzg-W|B?+F|7%;}lHAJ<if#JKgO7+hJ0g;w_Z2-_rjnL1Sgi<fK<w~_1Wi?cR5o`#Fb9Uy`gj=M7%JSmFCSkp2VCWa;=lsh+nJB2;tQ3rd(UY>SM>h()USvBe*H)=SU&goQj3gd^f9f2s8vLkUC2j(L;7}e95`BLCxbF%AEdAV&esD}_M)HLBVj!%);FDj%FSd3%CVibctn*wWmv0Oj~UaIcGM2f*#zmBW(Bp<UPgOFT{L&oU!JRgYLi?9d=33Dzu!;qGc6vxd9jzhUZ1|u?mP!0@J^loxmuzzQ9S4Rd!F;B0*C<(4dLyF~W`5|;X5+%%g!q{9|=#~&07sx`yfKuR^xeQ!meyka8V}$I(LD`|JTYy(Q_SF^Ygn0^rcV-jE)r`+sI`LW5L3iZNz7xYR^gtBf-Gr$a<`yoBlwr*&IEk=>;4x~Ljif28<W3%{**_S8N)U=`GyX_|Q5(6GzSEt#wyC_1LuNrZafK2484iQb<EX6B(B^^B!kCOexnXs-Zaa@LCp?*3ZdNvfHGnTK4&m-WIhREnXL_9GM)-&~2Wm34#z)E{pzKB--6(u5JlSuLm>b?_lde1CXslwK=&4=RWDa~;azZA0TQmU?%T|z48jn%Y*Jb_l5Sw4gY;M2!=VD0o&7_8w?Yjl$LIo0o+Vl<0j`&s^JueVO(i`04n`aB5ff9t*(;Yh1amSImC!YXF(ZeAeDhdA@AAFx%Xi_Kz`OxM_S^EdML~n*&qBxZDm?GD(#LU@iPEj*FWFDqM^dilhb!Pf({}<C~4-Od=Tq^7_+Wc)}h*dzDbBtT$#v`#PQZP#!fE&gaV2x`ytGD7<DFZRz-@3p?@T0<YclHP(AQqzowRZeSM{7Gk_U8NPW=TVWgo9RyV93EK_hAU*b+`i#G6~gx(TfKyTZvy%pu0|x*1E?dR}q|U>!qOic{X`I1{?U#`o;$<m{Lg)Zi;8?J%rE>Q`xHZ02^O6a8Bkk>mH`4E}m^ZFI@wFa}XFbr-tEFCX&X(fUrVLo|p?a*wb)l@R5JwsNBsQ!7`Q}1f4fYdG+P@>ji<PyCr_n31LLANOv^K97{D_5uihAWWdFA7GO_sx~W1Ir~$_~;|AwC2oE23Vce(ye;8I9C^BRZ_L8{=WJXA<V_iYv4+@P*g7z4zC_kfZA$g{nj?M9*Yj+R%r;VFwZrUosG$utzpgc)5!NU9Xg6fG%4&m$fnmfQs{&Z5B)P{gdk3YJGx~H|LRAn!tO9PJ=9oi9Qx8+_U9a57=5BKbXaryYO0GpJ4JH1D$=EYA5xkobikg*TqL+<sA>3k!D7l}=^Q4Ts6`<CED$<!i(E_=uGK_(29qM&((l(DK7{w9BN=GeHAr@*U`MHn+oxhyrxos!6PacCY-iVQeCq!(I9+2(MQS*rFa;%^c<^k%r_KCZ2cSdA$sCR2D*1X8uiz@f1$h*l>M28U+{Nseei#?cxfxCSNtOAQJhTdb+9$*q+hAh-^Z{&3iV2LvINi9=r5!R?@q1>K9D)@L|moB*?d3OwGD8S{6HWc87TA(%tA-S%N%ozI1!)g|154cY3e2cdWY-Ei`bW>gEYXerZ`!?&rug`qYHE*2)H!rfc%t?(*!HdCnQ`k+jkI}1RR$P9i&z~D-ksf5^NjM;Jw>BN-0+@t}=vFwKWGYvU++x6MtW(w0LnEVTg_8`Jppi%@CnnY7Ak}#5B@bez~CPoIbwA5QWf{_?OKgV7`|H2ER4XA2sN#-g*#@s0{795aek8=>PD**^UwlXWT3yP3h{*`-0SU10Dm>}DM268bBfvzi0oK;OX9T~z}VGPZ{@=|(_ZZ?b9O`N0c<z(m3pfmDGZ{y?Vq<1KQb)Qn?nX-u<)DS{$gj8{VBor#Fa;`|6z|LnB<UnDx$@3g<7r|&b%ys=((H!!<{}j0tBITuKEf=*pWGCoU(p{jU%r-}jOquWDp?yIxWIUQ|3mcU0a{P}x+H1_tpct@lArhDp$+EJ`*i3A|UCM|F2BklQGvatJXOxRUDq{n@Z5(<MNA$d)<LGy84@N6ooiLE<aSqIZL$XlyK+>hM0{m=4*VtqJeWv85#x5l$USb~(Pu=*#V~!*7`YSnuuiS%E?R<!|zXk&b@=bL5Nh;?AieuI)`2CcmZ4YsjM)Xujsh&p$@m2-wz)cN%Qz2qC@BNIV`xx4g!xHfTZ>d#{@*C5SL>fn|nZe=6E^Z-Y+jSj|P!*qE9#X74L))AUNzDR;pe>df9;A&J54<83fe2W&p_~rS@Yyw>pP1=09>B7_u^p`vI?5>&3B0$V*f6d{2gi2dz2%#}K^e>3)JtSmbSz;=iL@)i5t=-p2Y+YX)T8YU!+xvaOi<w&=-|Iez2j>doVO2}y+_X18xKz#gr8LG=4g!%BuY97flHMFk1jR9?C~~g+ZipCzj*NB*4tVVt^I7`-~K;sWfY|')))

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


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
