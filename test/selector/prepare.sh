source ./data.sh

mkdir -p "$ddd" "$eee" "$fff" "$ggg"
for f in ${yes[@]} ${no[@]}
do
    touch "$f"
done

cp "$selector_dir"/run.py "$sc_root_dir"/selector-test.py