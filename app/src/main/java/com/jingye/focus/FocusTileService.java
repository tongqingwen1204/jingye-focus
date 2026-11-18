package com.jingye.focus;

import android.annotation.SuppressLint;
import android.app.PendingIntent;
import android.content.Intent;
import android.graphics.drawable.Icon;
import android.os.Build;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;

/**
 * 控制中心磁贴：下拉 → 点一下 → 专注模式。
 * 系统在下拉控制中心编辑里会显示「专注模式」这个按钮。
 */
public class FocusTileService extends TileService {

    @Override
    public void onStartListening() {
        super.onStartListening();
        Tile tile = getQsTile();
        if (tile != null) {
            tile.setLabel(getString(R.string.tile_label));
            tile.setIcon(Icon.createWithResource(this, R.drawable.ic_tile_focus));
            tile.setState(Tile.STATE_INACTIVE);
            tile.updateTile();
        }
    }

    @Override
    public void onClick() {
        super.onClick();
        if (isLocked()) {
            unlockAndRun(this::launchFocus);
        } else {
            launchFocus();
        }
    }

    @SuppressLint("StartActivityAndCollapseDeprecated")
    private void launchFocus() {
        Intent intent = FocusLauncher.resolve(this, FocusLauncher.TARGET_FOCUS);
        if (intent == null) {
            intent = new Intent(this, MainActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            PendingIntent pendingIntent = PendingIntent.getActivity(
                    this, 301, intent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            startActivityAndCollapse(pendingIntent);
        } else {
            startActivityAndCollapse(intent);
        }
    }
}
