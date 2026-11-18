package com.jingye.focus;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;

/** 2x2「专注入口」小部件。 */
public class FocusWidgetProvider extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            manager.updateAppWidget(appWidgetId, buildViews(context));
        }
    }

    private RemoteViews buildViews(Context context) {
        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_focus_2x2);
        views.setOnClickPendingIntent(R.id.widget_root, clickIntent(context, FocusLauncher.TARGET_FOCUS, 101));
        views.setContentDescription(R.id.widget_root, context.getString(R.string.widget_action_desc));
        return views;
    }

    static PendingIntent clickIntent(Context context, int target, int requestCode) {
        Intent intent = FocusLauncher.widgetIntent(context, target);
        return PendingIntent.getActivity(
                context,
                requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
}
