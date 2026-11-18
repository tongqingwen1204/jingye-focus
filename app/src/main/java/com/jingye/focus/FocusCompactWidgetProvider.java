package com.jingye.focus;

/** 1x1「专注小格」：一格空间，点一下进专注模式。 */
public class FocusCompactWidgetProvider extends CompactWidgetProvider {

    @Override
    int layoutRes() {
        return R.layout.widget_focus_1x1;
    }

    @Override
    int target() {
        return FocusLauncher.TARGET_FOCUS;
    }

    @Override
    int requestCode() {
        return 301;
    }

    @Override
    int contentDescRes() {
        return R.string.widget_action_desc;
    }
}
