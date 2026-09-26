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
    favor_cow=(3<=day<=17 and 'YARN_STORE' not in shops and any(s in shops for s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP')) and prices.get('MILK',0)>0.9*prices.get('WOOL',200))
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
