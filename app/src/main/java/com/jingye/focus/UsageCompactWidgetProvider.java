package com.jingye.focus;

/** 1x1「屏幕用时」：一格空间，点一下进屏幕使用时间。 */
public class UsageCompactWidgetProvider extends CompactWidgetProvider {

    @Override
    int layoutRes() {
        return R.layout.widget_usage_1x1;
    }

    @Override
    int target() {
        return FocusLauncher.TARGET_USAGE;
    }

    @Override
    int requestCode() {
        return 302;
    }

    @Override
    int contentDescRes() {
        return R.string.widget_usage_desc;
    }
}
