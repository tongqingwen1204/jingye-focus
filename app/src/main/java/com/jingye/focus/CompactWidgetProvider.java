package com.jingye.focus;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.widget.RemoteViews;

/**
 * 1x1 小部件的共同逻辑：整格就是一个热区，点一下跳到对应页面。
 * 两个 1x1 只有「用哪个布局、跳哪个页面」不同，其余完全一致。
 */
public abstract class CompactWidgetProvider extends AppWidgetProvider {

    abstract int layoutRes();

    abstract int target();

    abstract int requestCode();

    abstract int contentDescRes();

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            manager.updateAppWidget(appWidgetId, buildViews(context));
        }
    }

    private RemoteViews buildViews(Context context) {
        RemoteViews views = new RemoteViews(context.getPackageName(), layoutRes());
        views.setOnClickPendingIntent(R.id.widget_root,
                FocusWidgetProvider.clickIntent(context, target(), requestCode()));
        views.setContentDescription(R.id.widget_root, context.getString(contentDescRes()));
        return views;
    }
}
