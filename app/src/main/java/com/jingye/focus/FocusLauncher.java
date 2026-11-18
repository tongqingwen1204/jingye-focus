package com.jingye.focus;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.provider.Settings;
import android.widget.Toast;

/**
 * 专注模式跳转器。
 *
 * HyperOS / MIUI 的专注模式属于「健康使用手机（屏幕时间）」，入口 Activity 是
 * com.xiaomi.misettings.usagestats.FocusSettingsMainActivity，
 * 该页面对外导出，所以第三方应用可以直接拉起——这也是「创建快捷方式」类工具
 * 能在桌面上做出专注模式图标的原因。
 *
 * 小米历史上改过几次类名，这里按优先级准备候选列表，用 getActivityInfo 校验
 * 「存在且已导出」后再跳，全部失败则退回系统设置首页，保证点击不会没反应。
 */
final class FocusLauncher {

    static final int TARGET_FOCUS = 1;
    static final int TARGET_USAGE = 2;

    private static final String MIUI_SETTINGS = "com.xiaomi.misettings";
    private static final String AOSP_SETTINGS = "com.android.settings";

    private static final String FOCUS_ACTIVITY =
            "com.xiaomi.misettings.usagestats.FocusSettingsMainActivity";
    private static final String FOCUS_ACTIVITY_ALT =
            "com.xiaomi.misettings.usagestats.FocusSettingsActivity";
    private static final String USAGE_ACTIVITY =
            "com.xiaomi.misettings.usagestats.UsageStatsMainActivity";
    private static final String USAGE_ACTIVITY_ALT =
            "com.xiaomi.misettings.usagestats.UsageStatsActivity";

    private FocusLauncher() {
    }

    private static Intent[] candidates(int target) {
        if (target == TARGET_USAGE) {
            return new Intent[]{
                    component(MIUI_SETTINGS, USAGE_ACTIVITY),
                    component(MIUI_SETTINGS, USAGE_ACTIVITY_ALT),
                    component(MIUI_SETTINGS, FOCUS_ACTIVITY)
            };
        }
        return new Intent[]{
                component(MIUI_SETTINGS, FOCUS_ACTIVITY),
                component(MIUI_SETTINGS, FOCUS_ACTIVITY_ALT),
                component(MIUI_SETTINGS, USAGE_ACTIVITY),
                component(AOSP_SETTINGS, "com.android.settings.Settings")
        };
    }

    private static Intent component(String pkg, String cls) {
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.setComponent(new ComponentName(pkg, cls));
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return intent;
    }

    /** 组件存在且对外导出，才值得跳。 */
    private static boolean exists(Context context, Intent intent) {
        ComponentName component = intent.getComponent();
        if (component == null) {
            return false;
        }
        try {
            ActivityInfo info = context.getPackageManager().getActivityInfo(component, 0);
            return info.exported;
        } catch (PackageManager.NameNotFoundException e) {
            return false;
        }
    }

    /** 找到当前设备上可用的那个 Intent，找不到返回 null。 */
    static Intent resolve(Context context, int target) {
        for (Intent intent : candidates(target)) {
            if (exists(context, intent)) {
                return intent;
            }
        }
        return null;
    }

    /**
     * 给小部件用：必须永远返回一个可用的 Intent，否则点击会静默失败。
     * 找不到系统页面时退回本应用首页，由首页给出提示。
     */
    static Intent widgetIntent(Context context, int target) {
        Intent intent = resolve(context, target);
        if (intent == null) {
            intent = new Intent(context, MainActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        }
        return intent;
    }

    /** 前台调用：逐个候选尝试，失败给出可读的提示并打开系统设置。 */
    static boolean open(Context context, int target) {
        for (Intent intent : candidates(target)) {
            if (!exists(context, intent)) {
                continue;
            }
            try {
                context.startActivity(intent);
                return true;
            } catch (Exception ignored) {
                // 部分机型会拦截链式启动，继续试下一个候选
            }
        }
        Toast.makeText(context, R.string.toast_fallback, Toast.LENGTH_LONG).show();
        try {
            Intent settings = new Intent(Settings.ACTION_SETTINGS);
            settings.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(settings);
        } catch (Exception ignored) {
            // 连设置都打不开就只能停在提示上了
        }
        return false;
    }
}
