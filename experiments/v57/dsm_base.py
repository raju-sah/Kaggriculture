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

_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-q}vU2j}ha{Ma>pY<TlkhGFFTAG!GrA>jPcCZly!@%w$K(Kjm@)qR3M>08czpA^c`kXtY^RQT&9L>Gwt50`zb@k`}Is3=2zy0&?zn%T-cc0HbUf<uJeR=iW*}wn#pMU$WZ@>EXAOHOIxBvM2e}DV0&u2e;`s**(KY#e?`sVEGU*6vCzy9C(*AG4Z<>TG$yH9T)zWr(c<L>&~50_uQ{O_yprce3s_RpU_PXB%U#QWXN&G-u+pZ4R2yWN@aQ~tigU+#b0?Y_OzcKNzLeEM+n?w7Aq^YH2MTZeZYkLB<UkKfLJKYkbVX+96jiM_dgyNl-a^V!e0cMm^4P7D5Vzq@}p`=TvCu-xa_avwgloxRxObB8yWz1D02dcWVFcDr};WnHX!@M^~ych=2&y~A@SyKec|SKq<6KAh;!XK%03<b8XO`)?EQ_4hyRZf<}6`opHf1U^13n4;-)qFpD=!u{>1>CO%20B>tNa%phO9eo~djPWsl`a2owVd}!^{P|&c=f!h>U+=<Xj?KXJ!|skgtvH{{ZydkHVYZ|95uSZm67cNf7X<@HqaAkE@vo0hFb=x#YRj8<azyeKdHS<5E9csy$u6s{i1_T$m!pe;Eknzb!-qt_TXE)>PnrKn&6;_ujJ|thTG9DvochHOpK}qQQ5at>aPpCzl^=Qhc0BIU!<Ro2(+<Bn{X+e_-`?Kb?A|{7@~7S1!-ty>|2Cht`D~~@y7JTFW!~N0emrv=Tr#-hKfr4;T)?@LJer$js1mqT;5uMay?mj9PX+hNXyW2WkS|7SgT5@ER3VVq%pU@$E&l!P`uHl~6UG|rD+~A8=qTo|G<>3?I}4va{M6(=!{HvCV=$BDzfptS?Bs7|vHJA)qk9X!3fw*0g^!rI&cIz59Ofa?V{c-|eCoQ69vn>4e1G-aRl`)2En*&=#51f%UL*pE$506AkP|<=@30ioo2yeZ{A5R^Xl~FK$K$G8c<2cWtcOhwa^%zREidXa^orbKbi!O$6g$6vJXf?0M2>)E4Ia}yRR}Q>d{%;wVwY?BJLWZqK9F=G;7H+^U9$}yHVg_55B@UtbhJyc?x2#zSRTVRxRm?D*;cGi5JZYgzB$A~L@*$6EXcgY?y+!d;Fl2bbnN<Wnq1}pR?;U>%~k|(d3-N&8xUBci-kXZ|8RG`|6zA`_gDRe7oH2;V#=jxz6<hzkV}ZKhaa!+{^D#w_Bx~Qqh?&2vX-|wx;Uc`#_`AS4s*=T$FEDv2A?}wq2Sk=fhX`a@|u_a^K>San2at`e(mS)HJY;Hj6B=RjI2JKuih_4mJEb#J<e3ai!l3qs`r>2o?zcd4;-&}zw={<MQ{t^e1sM&G5*E6v62?l=0QN@0P5jN2DPW@b`&pVK9$X;+1M@#iJjy(2w-gW%#wNIOD2b4l7l?@4jwsVE)040;mef}Cfg`5fXI`(E||YO_!mO#5?m{A*KF)v<4oTO+s-2#Y>j)n6D)Isk0^>!C5NKZF?EAU=G}XdV%x<JlN(@FUA$`3B}$xA>oQlL?9mhZPNzCC{;SoG%c<PWm$j6JUwFb-vElrt1?iB1Q=hPK(<@oIwVrj#fytRPwm<4mQ!`2UnAkDX#VS;%B7VB{Vx>aHi23P}N7kPM=7vXbRt!pp80wIaRod4%alZb&0((qIspMow$+L$HeU}%I&r+41NyFRv9F|8aPhr=Q#?gQpGhpIy`<tPaN9mB<1qf3`T7(xAMvzDL8)kx7S17HO;YcQUc;f^}ZS!FoT!`GmtiSPE-&^$@S8}v_xr4nuzxp@3sQ3z8q0NchzY5IR(<iJzym^)Y)&(Krp@o2Vg18H>)F0ulKN=#m%WBRP(#C*}6nQxmp_t4n(Q#V1YzUg<^z_n<H03H+odmuv4C7mW0v7D8$_<&3uhg-YpANTL&bRh*IJV=cZn--6r;gbTQd@vV8${}b$gPi|_VuQ_;<bN}N1Xsb#XE7=m2%Q$Cj#@aJ|ExkySFmcF)L^~Pk-+d{0l@8QoLcjL%CuK6*r)~>@=MVpFCwjitOM0?d`Y!zpBX2ARdI^-p{Y}X8aw+I>T2FvlhJ(<{%tahB_f&G7pF6=KAM%XBuENJWdN1L}EJL!)o>+99S#~6@YgCZ~rU>y;!v>bpMIQ)%dr=J`aG&#lI5kYRyvyi#$+#X=n`0x7z#L+xuOU2G!^-AOHIH_HgQki5ecGl09rnDcmDS@hCgx?>@W_D9z!F$5=a><w$;~l<f)U*Ze&yA%YWtzQE*&Ws|bBfD#fkIvjN1Q`0)zt~rN#hNDp<pl*Q*JrUw==rWo<7HKvmXHZ%0_N?AHv@yf73<Ct#2TlaOtK&)%`{p$zC8E;?&69i>bH8Z?isnN8a9AT&nIayq#a>=#wa`@oRz<NPL8?C&%<53zg=2L-!_08N+itwty$O8mdY!Bb9$ob5`6~8)b@;xyjZzG-bO@R_lhKo>rx<undEx2mFOKaxVmgaMGz?W+K0u`a#=q6z-4`W?rd{`$(!+eE<(jKx69z9UCzpjhX9gn_&^BG$>tZGS2M+RZ1*&ct@S=`Hu~tr~Z*8b=2|dF6)$ol%jz>?%fyl6cHzZ%6*1|9CWaQurFH{pwMXFv}T@QziU;(ulvt=npC#8Y560252PDzf>@*P>!Nacu3E^3rw&zw;eeWWq7j_?K14r%NX3?<ETdF{8~RvcR}jida2@Cp7eGyAb^uxJustNB|alQ1~WWx$Z2MI|W)Z;5$M4aSFjr7(FoTGl3)hG<8^{RJvLGhLacf(GRMqVtXZs&PB>%NRoumX+yH3Q44pKxz2wG$C3Pq%hUlHR_rv@NX`+YeFOd#~Dkg=h{fFD6{w`@L41R(6)0y)l*oTGy+(UwN5=*eak{l%jt<Y@zwd$hnqh?W#t31ah-J21->{;&gexI2~g?cyl|T{iLM}{|1_xK^I&o~x>Nas^dk2JS=wSZM5}?m2TDUiV^-E=4Ylei0|~#Tj7{`II87{Qpa?-GSRgWzI(x^H=?au<Fc4oOoRhL=I%ib1<5|L%fLqCn7i~CeVHd8#ECW7#$bl-ia=56V5Rl(EdYR);;GQ><&3cpu-H$@Gva-|N@(R{-B&l)suXO>Zs<$u_YNkieC-uCkz!F#M@21O5;#-(&j~#dObvF)U3)^?}(pp)XIp5-25(*VjsU;nudMGsH7=x~UY<81C_g#8_Dq1o~MpxI&kl}J1v!%WIaP+Nsj!bkelfQWNU0%8te2rHC09O*-DRA2GLI>Mjhy84s&qNBr78vSLk&`JMNO>>2Sj{Nf0b6N}${m5BYLx9@DmrWJw3Vu7(7#jIAB`^ETw*Y6II9!`$pbUG;v8P-sr=$XNB~dxemkw(0{Yy7=|W0FE?CVA=XMP7+UW2hm?4s|gyTrvb~>nDzz*rA0>c<hzO}7+r_268o2FXm1tPmO<t6~xk-;di1gwe<B}Znk)boDi-HR`#4}eAwE)4Q-aMwk#(Wf;Dz{p?v0>c8>W>V)C-YMs>I63w6UOPlAk3u6-5K4H^M<*u6aH`~%tbS@bLvZH?Zgpb#glXUgz+cJvUmk9Mx_-FrZ3Yn07;b9Fpjeoc$1iw#)!DY7J3y=nal1p4A;R6t+i~LPaS;}sb|1j;gVT-!AMVS*e9y!YGs&G@F~h(NkoBi=G~Cw2UN$zjr(B^)p}5%e9`{OR(6j{|bUdmwlMhcF{-_|psjXD=Sq#95d<~(FsaCt?CZaa2t_8&H@>hkG<Pa1zh$ZqMNTXP_;6;L(`J(hXJn1%pb;8-YjSXLhW_MhI!aj1A%2*UpIz~(J#oGj*0=KZrA}&o%{`aSp5qiU^O<R!;?f!mGsWpW%t+nW0kgUaMow{I=L!3&X&2z>w*`};7m4lMAMv<GUPe3l7FjA80r@_gqVMuI3dL`+!6qkKMdM-x;i`1<GC|8KKAE&CBi-m&JC?zWLeuRcg!~FGh15n|Fv>=FsGx-2(NkEX&MpbELJn#}lwgO(fcqqJ8mgLaLn^{93Va5c4))??&wB19S>P;1--Ck+|!(@69maG}(%eVq&`nu7vCjZpMaimJ9QpxHjEM`HKVbeDoZ4h*-18h{7j`_a1I$eT;k9zn7QrZ*t44f>?;Caruf@TMeGb<CgOznR3c~ZMJ;^USlNM)-y9vJsEtjgrPw9u|dOfZ5V(~b;E;9Rke1PC?WB??z)*}V*WHZG&0876z5{#nAIigHLxmPlk$XHSuZB$jp{m<6IJ!Lwl4!GWMYv>Qp3(H}ouqCLU5;rm0j0`MuA&=eJBTU3E<Et8FEHOVbSM2+$a#()DGqJ$kGJ?MSsv}gvE5uVBD&oiqaDxtQnBt?WLM4xQ2BBew%A3!<_v~kDtEk{-cqRcRo!Ax6mjqL^Fa54!a90e_4yF0hp#L4y7>({Je&B;Kv#{GSYN?v%?(E(_guo4<k@N-dm1|d2Oi{S`~Fm(c*wLxmv6n7wWP}tm%r2B!7kel2xJ+a&ole5*P^b1FW9}@z08JrMJg?mp}qHR|FT}H+UB=$AwO*0XWW|X0hvj{>$ZJRz+SlFCt3w?1^ysYQ{L&}7DI5CVc#V@*{QT)8Z%ywX1QPM{^FbGI?PIDJsc-9Fkh(rP`L@;L&W(A48D_8-ljugQI_(#SK;F*E?sn5U(E2?)TuX6~KNmr9X%h?JbFkAuos+MQ{$wLv1AY-Z1q-7bkxhFBj-%P#!<je(CY>ra6#0-j9z_XFzsrtQJN1geKM3#8>Xw09=F$9KD&^UMg)Miw0-6KGtg;3xsHsugXpM8AxpQ{m2<#Z5o5{xQ;QGlU}B%&21QuU)f4+jkWOgNzAlk4zJqx7_A#)I#}JMWaM1;IX6U(2YIj4Hk6dXeo%HtK{}I|njRYZ>jy<uG=%Jq%I8*|vh8!3Eba-?{iWIujLex3pGK-=cO_^}=(F+{oSg_XActk6+b_ch+{u0j{aVXH8_fq1ggO;1n1)WUzN4EC&RseN4+U>gpT>+m}H`0C$d+K{Z&w3@-qtWeSL%lh}%^;pHiQlcgHU7#x=hCyYo>GmLdRei?YVT&E4LHVITk^Dps~^Q1Z7s6kF3aw!QHX#P`y_?}CHhXSq1)hZ(7?(gfQc%tsX0;)t8)jnL!jR2wZjcjvRLod=z5&_vxyDT^g)LVh8fY!LJ;;klX%Z`pzUeS1hR&GpEHn48X&_YS7&~FX7=Q{M;29Cpw2c*$6VvA_MP7dzndU*m^!f!%|A7oAduMTN43b|4jHUo3CU9Or1Im$xM!Ct%F;rzzHmf6Ewso0Xy<kO?yVj;DFH<CaTYsE|#A*MYrqiL!T1gKSx=^J@NcMqj3$M%EMJ3X@3-6KIUmhh`Mme(j_On4)q&~5I#@|%OTa_x=DQs@qi$Qga2Yug2Wwo+NRr4cpycsQ~R5PWO72jmlYwejV+ix@1`b&p*JLXUmKqu)R{x;01ds2WogD&8SgRQj^Ou|9t(_;Zb79hLk!d}~P$a#N>UmvI8tX5bWPvfpsghJ;C!h`6d22>g<fU%alACmnjT{5cIh#&o@0udOd@NiSwq!TX}U!=WseYn5=IHZ-@^pE%%cGtm&a%#G;>Px3_#z(P<p0PSJUU5<vlU_CA7hz;_hnQn~u)Af1@*>8*|j9h`|ry+`>t*>MHlqkjEbWa|+VUyRgFU*Aw3hLY9JmKEMDGf;bkKAEqrtH=ij?#^Q83l%je<p?kQ%f^BD3@OvwJ+Ir;x&0Ct$C~KUqIeyl%ED?FYf}GH7v|A_Tcn28V^BbMxahI5OCjuJat9Mn7D4<H3Vx7h9}laoJ|_W8rP#;fhcyLRB8&-f7QrTB;3o$ukox$N|h}DI_Rab^i3`qFC;434nFGZCggw&p<*}zYM<UCGE!*YBx_1X?nLDBm@83bv9g2V$o&=wt3}xAX_Q|&D)XLSV5D_>`hMfvw2f9>yMdKGo=~r$(0?3tWe<Xn=uC0f&}FA8${13{;>x0?LQQyD-OPu{EUwd?sv}yNt94K`30FnTwoyzz2_Y7UO*ze-<L2N_po$PouD`7(@;G|40KTQTXlreGt1q0zKIZs}Cj()J_j!~HvkHNvZ~#ElG)k(>T;S{S`On3y;Ft>suLu)X;9nUTjbmKW+YA0uy5GnZG&_}@FnmUJbR#LglZYo{0xIa<%&rLswP%SLRLIaPB=_pHStJgZHWLc!S@KHMe*`d`kh0+Dk+Cl{Hdj-kq+)@IGwv+K%ATtOCy(D@LMefkaagZDSKl_=DC9jJ7FR;w9tN3Wf}sjZN9osqIgVsIiU~RII{3`G3WY3(3@GiGq4P+ZO!(EHuQnaTK<O#kq!8p3fHq2iiw*MVFDvB@SUrhQg`fe9$<<;Zb0uzcGTF7FGJ}38AdpiiaEd`**=RSbh#~UY?307+`d*3Nzy^G#MrJDb?lL7gsXQsqE&v(9cIgF_l5Rwxr~T78y&@){N#fGwVMf0v*Z$K`ygL4a0v#i5hVPoPbE4!Gs~;m8gLDQ8ot+$Z<yctlsNgqx{o$89vWyGV{ZSJ6M*^EU5n)VC1$!s)1gKwH;gLC9Rnn)=!~<NawuFGzDz*0p!BEIj@H0)W2e)<#p{|jCPIIeyU-`wsZjm+c<pJ6XesL~h34zk0AQ&dPB>y6mq*OZQ)K~lNtyI!qcC4g#YKw`u^<F;+jGx)z05Dw-&$<%fO5Vydi^3}wDpXS@ItTPeug1m6T5MV{N!DTn#s>kxJq8QZd|I)sB?AreT^5=oMrAvpQ~^`HlvIK}p&HhO_9aOWNNU_PW0mI+_Nhc(?$g6t7!akM`jl6{qZP~l`9!`P*S2LXLKB)XY+l4RVh6rzA`>{A+Q?R+@)-GJnGKfTA#C9`>q!6S+69A`Z3WGFwSZH$pW6m=GW6DCv`vK0KaR0%sop<e?rt=gIgX)dk$!x(^@iO#Klw{H6@aHWE@1CoJ&!6t6JuB4nigbflZ<H**w<L8P*yf?odX9NWz9LiEEQ#S)Hh1%0FF{BVgR@TS;9x;EJwSHfFklhN6mZi>>VN*#lkoW?Zjvf>Q0Zi#qXTEDb+}t6fzU(2e;QkzogWf*fSh-fFP4fZ{|j@oY>*6d)={a&zS%kQ%Y5xIitA+w(Qiqo~4$wGAAu#Mj`EX=oMYO!J0;!8FI5-?BT%HDUVc_-N+>ceAtpFDKra2&LR{OqO7H04njyn2XtC_log?5wptC6Da9zYBZ-X{8t)C6c?Q+AVk`nbmIjZ5=SE7CrFM>l1ZPA<ZDjPACJ34)2d(Y|WHDs1$s2j*@GV(w7mT{JPT#c19U#g{R*H<s3u%euK8508ydz|j7&fJ0Pc8dhaN~5{ffzND_Iu;-au}Rivl^b9>kHMyAvmWO55{QomLcN)xiKwiv}4qM*AY;ihLW0q8U;9YA>~}0P=I5d->=j%j59UAe;#PI9gW?lpU)MU9NDPzRrteAnypeKWFoblDZ;BtxCUL~TxM2RM(_*KdW}2DUByPtAPj4Kru_<9uL32w)Wt}tB?w81ej_l}SV{^vp10+fqcy~8@(f*NoBt=7NrL)IAs=pn7f{j7J(R~Tm`KO{j*w9(AD3LZPW6<n3JAfDQxF{Q!aj|`y6YC_t*!LF;H>P;(oJbZ{ktS91(7M?BLcI(dpB*Sl|Y~c%*tlv+wSdm)o}ZH#QcizgLvok%w*uOj|O^v4z;=SiY$5Cb}%(*O#yu3Qrf-XC066D1W$Eg+!j5|@nL+rc6-6Ux^Aqj2k-P&r|F<|w09&SUxmJJaMas2Z&A9{xf${^kWF3<Bz59}T3JB)gvzPgd}&ZLhAwR;0IGacRt-&Qtruc_d*D119)@(mNkShgT56~%=vd$DXOmh`_2KoV+EUr~#g~%_Ct$1!lU7GbYei}za{f7Nm~mHQP`XBt_Cz?5ltM!vFRS~N7m{U6N?M^`&{j|?^boy`hQfhE7}K|UsytdEqP#|0_&TSN?i{7)gcv!5&@N5vc=?Q1Tg<ZuZVH@_A*SPGPH74nni`98?Ng}dEGOqPTTiH~ZdzEddPoq1IZRx!PnTCn*hC(J!!Rfx$Z$mnAv{pxlQqgAP@>7Z5AV%3V$G;)1HuC=suUqk)T~l<Kc)_vGF;Z-4f$C#7Ie`@dpMZsq>Dn1Ebk`+54Bg)lma^)6*H9{Sr8*0f&`R<B`43skV}07q;m%$0g_5SS|qOxy>N@Ls02oK4B=-gr#rQeQml^9lSdB67{rxsI*N+x5Ez<xIPlevyG4q7f`L-n;;2Hf*9nVY1d-^9?&#xO<PzP&vQoKdI7&odd{bk9i)WKN+U(R(5H~muv5(}FSHnt(Vy7&|x1~g6x532>{W<1qE;XTBDzHG|LZhFpVh=QX#K4?(#P;H)Q(KoUfL36$P7)fca#aIfm5a!@rS>nBxti0pOm;2>q5d$eRd!8qkXk|$*5|Gw=+`M<CZ$LT8M+g|njdQz{<HFjICbZ4lSVNCr*9hq=3*RmFX!7@sIADzFjWe@0X%8p<zlCy+*csJ#%A1=s<4{mt%IXlN+f7WvTAG^g}C()q9934(t-(oR(OE<T^bX!738CZQe*@W1`)p0&!yDnJtvb2BAwXWu{Pdi2x`Rx2%>+tn2!N@)r^Hg3n}U`Fl}d1jj?#9p5~n1%QOuW<`RYGN{o&<9?RFaySshBVfb>cu?OijBaF5kI$~u-jY&@ggK4VSer)-6i-TuE{0ynknopL6K_DEKr~aJiAQk}btI295MaTgfQV(Qlq?Sm)IB239JFWprsxabzC=us2u5p0p!ePc2#g#}rc?2S_P-#7;lD-j*f+7G;mS&t_IPARm3g)ihGa!_&p9i7rg``ElCvt1gfmcSaT980>N~pR1sncQ8%g2(A;HvT|ADYD?uz<=YV5hEhDi|kA;IyUZghjz}#Cu(sU4|jM5z!J1SJO5{?ihp;TI5ZYo@1p#SuxKLJ4HO^FjUk%R@!M335EzNtzit3Sfcu?MJCBJ4Osf0)Y_mUL%2g~Y-pA@bGB}TTJk+E^7ts!J5)x#ZfRUZn7{Q*DD#Vt8~h2E=-QT?<eVWeNtuzXFsXsc#Nt#+U&O9ptexw%O1Gsk0_#m$od_-p%M%p}?m(;#5}k)#8sY~>nwSIy^{bP&R7b&ZY}GvY?r@&CJ4-QM3&O~px6&O)>SK9{70t1DfT~vh>(tk0pfI#l*b>3zSF)duE>=FrwLEW^@_78wl8k-j^5BU)z7U2^Ckx4_VpPC*WE26Wi%QuGYD0xJtLycyo2ilqxCHS<qFyPFxaj74Oy<P4^jz*NANwH;<voI<NJL5~w%3_Qg_7NZ9?{rqUmZS$`JsrW$#K;QX19I8oX;YAzzTc(8o~a+^=v^zDhz~Rx8m-pcS#QruX@QdtJH53F%&M!$WTKV#L1-A*=z`R6P`Rl9f53x7vskn$O1341jrT*02d7ko1+NqJ~4q_$@zz16ANEM?^kJY&{(xDIf4dpi+QUYQlJIvc0XyO(~*?I58#9>5Vr`|rPJm$fF~uOPCsqErFktll+b&(Dw|&widL^!4p5-8vZA*j!j~jHbMkIOal8>GGSotBUfuP+;^0IGl#s?1J&u!eL#rqnJ@GJEL@g@;n1ysF8%;xm8{E6R&;SmwR7cGaO?V<CPbbOFiCk8h+7+K8q%;YiAn-N`B|Jl^?fZx3gm!8^!X|p_UntgFY@18F4N`FI4JsVHFmWDQi6-crp_Z`=0D9ep2Q)3$1DChY2So~g!dx1N9pUPhv{3^v)72LJczu5_QDA9oeE24TEsL)}GT=m?VVVt7IeA^+&_pcq@}(0>H@xJ1D|K_L$oK;3tZoET7-B@@r+F5LoK#4rn?mpErb>9R<}jovQAK3xMy<^-<zQe6ha>?k&w%$RX74N^O3N7?cUQ|ZwUA0pkqU_-%w?Dzq_Yj52Iq_~07<#;1uxw#PbCulHGZ`Vgn11*3Mr5vgkGA5)IAZ9W20+N1LWV>&?H(Xuk?}mt12`^+CvdmC)6|}eMCK7NGdXD$$5IoxV=*gK|WHrqB2cJ3ASWJn7+E??a6YB&=D`P%}<qKe36O`b@ec<laA8pm#ZI|qE3LLAIHP+Txnc{#oglTynu}sm(va_p6ced4c4bA3<1${(jZ`ZSn+616UOi7>nCMx>x6n)vBTf_w$?LTI3Umo75*K|K{fP>NgQ7G)M%Lk8%XN?{ia1aLjV=)ldccrDB%da$wmL@7#1>sM-1|fjzOOLqM1@I_BeKkLk9MK*b3??%<9P>$9=IX@$v;LXv%OR!@w0f<q6uocaqQqBH-=R$xV$qIafSbNl-KI8KKzdUebLhlFY0Y4fa>eqy=obXeQx$2BXibL_0}jsvUe0qT{Vk6QQ>aP=wUoR2?EJNc2@sjf1vAf9;00Q4Y!&h3>2AZOX}($fL%A6gqS3$Y~OWuELI{N&qXI!@LTrt$nucU9<Q+!;GrkT%4LntI@O&vGcxd1@-?z5(ach8oM3n-iSkgr5iQy@?2PXWqC~|`-%_?TF)HJuF^g_Ap$IUE5_vl>fd>sU);eGp$lVhZiPD(tIIE!y=rrv46-c{L7-4Vw5)Z;z<kJhwSB6|soj`B)0XEPgib|Dp-WBf_uN3RNdAsda`Aexf5ohqrSxl97z|VDEw#vG5z@CK<J?^;mRbs<`FqwKtyj&um}=&xjxmJbXLJ6BO7JukKexW<M~)t&-%0J^<4aP@*g(XKBc?}R_ldWCa=28AS<)JGBcOl&!gJg#9!Ib9&tA6mf)>z#Zn&vL%6wf`EZC~75RRy?+gDztXE3&E=tr<N2u^#Sa*^d64sEMS)C4W5erA^il$8c~HSKnVXw|4?G&@7ok3|dP&}uYL))d1KuFf%2@6u%^w-NFUYXylApq?d<JJKr%MT2yx(A_blanTUm3;8@$_)T|In9<0zMgo;KJUwDP#!Zm8=R!*#*1Sin=xc5V#_REvqpCNK>ejIwRw#M^zMhz%Egl>oP)mn4N*N>Ymxb!V*!1|hQia-Z6osR;SJmebKQ9@0&rNF;eQ5n25%RCDXW%5Xr=A!vVE}5vDHKV-y=(LhDldjO>D>Z3n?mYo1}}*_7L8W9LImn2-hQA|Jk}pQ9#y7T(5+WHqZ2UIi(C`|^E7hQ2lc8i<<SDyfq<gW1r*FNoJYXa?F0;?Xf10|6-YioWl!FlB0mu_6*9?K9jK_|-yMzdrAo}jL7M>i#$K_Y6)nnzseySFN`9H-+ig#A)2)CpJE{!Z*mqrlsjIY<lfXBpiPY*8-Qy|!m-hO9hyO^}yN*_k%UP|nbU96~tuEFP6{uHOauBi&5R<#x%lQ5ZZKa}Hf^TA`4(BolSJ=K_hLu)Ptol4ae!Hp?W&tN$yTNHoShbp!b|jB!LJ1S_skob9MAL>St2Ee#87C(p7M(Vw?Tc8<o*!4?`ZIy81Vx98qNsi;-y0>FhdTUR7Zs-E#H`&oh3LBqXbQV`=ToUdoZF!?*K?%j%~-B3yeB0hEba6JTV&R)1<^HR6bNJnsilo*eH(b<uvtCgJte4x+gZhHNfCXa#~ADT61I!+He>NVjU69&{!skH8j4AWP1TEQ7b<07rDS3l_PMXC(^&cwo}wz%Zci$++QcWg76SqqIkSZGRCP?%B@FW{a$aImwt_Laya&tnXdT=7M-^)nW4J5+%Rug3?BzUv5Fp2ris~N+UY(XQaY2J<2R4KES0?~YaVwm-T{HMFDNoc8RHTraqSYON)9*FlG=$w#{R0=Q$3-s<>`s{uMZsi4L(OUl&Kx4*&`W6UaaucxtmW}U54|#SaaN@iI#zodG8L+zKzrx39^!@&HVuSd1X($Pw8xpYDhGG#fk_zv&pG3qq%N?rs>`V}jZ1L6WLoqp$GxfjUn!2RH!=5AcU+K3W$^Y#OLLNWaI6anwG5L=ao6IOwu~~A4u_@H`r>JPt*)bsaDB?HqZ*V7nX*ayd_8<0>m3RFd9Qi50}{+T0JlKDN*4hl5@2)<OA*+PwIECu6kA;d_}FP&*ec@7I-LauHM5R_f_3&U9CcAeslkHjjjbm%ZgR@_LC+rzY7)D8Av&_P|0tQUn!fKST;gDDr3O=RlO;-Z-^pU?e1U>XFHdZV$R&4r0;z|k&Z>-IW<{X|a1A26!zI?MP9Y#tKylhABF5;gRJglc6{syM43q)QE`{_fuw$QJfdTSiks6dqg|+qeTmtNBLJZrMYE^jOGgVYV$SYijx)@;<hL8Lb9#&@kGn)D(NhJ}HGotg=k|O1<EIsG!GT#H@tA<>^uzQ+B`iZz8Os^xNDBpcT9X$39T4Qh0%1)!-@#v|DlWk;H3k=h&3g8f%K_6Mz&KH)$AZ#V2rw*(9@@VOD!8qet2Enb^NSU!pc_6~NEUqBdkS6jBSzf)}S)Ad?4=+pX^eEL#+Fpl5JPEiFWmQOr?eP2((rcnWx2w@xjV52JXdhAoQ)q@l294_u3Py`{J*|`%Z+bEi1+I;r)hOn3`Z^F4g@(j+u5IA4^Gz*V1G*yO^~@dA)5v65kVb(d62{#(1E^z-&9ws|s{TT+nst+;iLyFSDAPN64v+IMQoz&F3t%w9VQx7RNSgRs-6rAUq8Xr<(uJ-hdkFx<Cpa=ZS3RQ8V1%&UnZDW+m+}G*_)WYMHloK>7ScO`RxKiQ_SLOby0h#g>L<CuxKLKB>H;Lc?oGzWKKIcwdF{5Kp&!e$g_36_485=zeWXft<uxS)@@;4>MQ*VIov}E1xkn*fwzwk7Sf**rzik0}g#HSw)++H_`3+`7h&YJqcu;w$812n0{P!vhOSqH}215YKN`a7C4VT;_Y`3IMg={Elb;*4MnnNyL-kw=O162h(o24W{oG4*RjREsND+P>BkQ(r@X*{|wr+F0G2j2>0>)Sz`!>cS-+?iFDhHzbDCwb+x!SISf26CSgmWE*6a_~|0YDd@&(9l{v+(}$kBP!ChtfRxlEmaGU4W>B)dn)ipX=!_lW-PGoIJuLmbLPR^aBlW;(?;!h$Yh4$T}LlNJ1nM`j9FjVBG|km##72H!ht#P*wfLt5T!!}T~wAO^cdfJqa$blEdc^CMFLsm41r(AXR><U!8?j87+|_su$3RDVPnk#IKK2{uF@t#&%>p(p&mUaE*HCTU@use1`6o`>I2`H{Y^4Q%;d^i0l{fzdy~Yg4CA67&68(UM2?l|+KQemBb+B=isj=}{D4}@VrP-Q2wSsUDPhS9yQvXYa-p$mz84vRCM{SV%vpCSVJ4MOI<&Yn)ZuvEI&n^i4l!oaF?_ByrnD3G`)ccSm$leF$}6C;eGV0=27y<^2^Y6#re*GC7|wdzSKuUPj+h9k5K4&CF-{`uP-RjniRu-=iL?lD1p6H?8uDsL<TdE}rbE<)e#czh$4{=jSw^LW;3rb#nnOJXP5Ck-c97_sImC!{L@IXCY6Td}eitov1DPfZRJLvpCG{tGgwPH)hPSbYx9QX(D)@Cgo<b8-P&TR-U(_Pfd?t9%r2f=&d2PPOr}mA`o;%NH<;(v8j|iKX')))

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
