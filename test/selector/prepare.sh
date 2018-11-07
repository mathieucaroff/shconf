d=$tmpdir/_dist.d
dd=$d/_sh.d
ddd=$dd/_host.d
ee=$d/nocrit.d
eee=$ee/_sh.d
ff=$d/with-name_host_pm_sh.d
fff=$ff/named.again_is-root.d
gg=$d/_os.d
mkdir -p "$ddd" "$eee" "$fff" "$gg"

yes=(
    $d/_ubuntu.sh
    $dd/43-gojusan_ubuntu_bash.sh
    $ddd/_ubuntu_bash_sefidos.sh
    $ee/whateverbend_ubuntu.sh
    $eee/xyw.abc-123_ubuntu_bash.sh
    $ff/what\?_ubuntu_sefidos_apt_bash.sh
    $fff/'name#!_ubuntu_sefidos_apt_bash_user.sh'
    $fff/'name#!_ubuntu_sefidos__bash_.sh'
    $gg/_ubuntu_~.sh
)

no=(
    $gg/_ubuntu_darwin.sh
    $d/_ab_ubuntu.sh
    $d/_ubuntu_ubuntu.sh
    $dd/_host.d_ubuntu_bash_sefidos.sh
    $ddd/_bash_ubuntu_sefidos.sh
    $ee/abz_bash.sh
    $eee/xyw.abc-123_xubuntu_bash.sh
    $ff/what\?_sefidos_ubuntu_bash_apt.sh
    $fff/'name!~_ubuntu_sefidos_apt_bash__user.sh'
)

for f in ${yes[@]} ${no[@]}
do
    touch "$f"
done

cp "$selector_dir"/test.py "$dir"/selector-test.py