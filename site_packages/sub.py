
def regist_category(store_obj, category_list, errorlist=None):
    # カテゴリ登録
    try:
        attrs = [
            "category1",
            "category2",
            "category3"
        ]
        for i, category in enumerate(category_list):
            setattr(store_obj, attrs[i], category)
        store_obj.save()

        print('カテゴリ登録OK!')
    except Exception as e:
        print(f'カテゴリ登録failed.. {e}')
        if errorlist:
            errorlist.append((type(e), e, category_list))
