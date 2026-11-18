package com.jingye.focus;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.widget.RemoteViews;

/** 4x2 宽的「专注与屏幕时间」小部件，两个热区各自跳转。 */
public class FocusWideWidgetProvider extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            manager.updateAppWidget(appWidgetId, buildViews(context));
        }
    }

    private RemoteViews buildViews(Context context) {
        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_focus_4x2);
        views.setOnClickPendingIntent(R.id.widget_focus_area,
                FocusWidgetProvider.clickIntent(context, FocusLauncher.TARGET_FOCUS, 201));
        views.setOnClickPendingIntent(R.id.widget_usage_area,
                FocusWidgetProvider.clickIntent(context, FocusLauncher.TARGET_USAGE, 202));
        views.setContentDescription(R.id.widget_focus_area, context.getString(R.string.widget_action_desc));
        views.setContentDescription(R.id.widget_usage_area, context.getString(R.string.widget_usage_desc));
        return views;
    }
}
