package com.jasper.labplatform.viewbinder

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.drakeet.multitype.ItemViewBinder
import com.jasper.labplatform.R
import com.jasper.labplatform.repository.model.Image
import com.jasper.labplatform.utils.ext.dpToPx
import com.jasper.labplatform.utils.getGroupColor
import com.jasper.labplatform.utils.setRoundedBackground
import com.jasper.labplatform.view.ImageZoomDialogFragment

class ImageGroupViewBinder : ItemViewBinder<List<Image>, ImageGroupViewBinder.ViewHolder>() {
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val container: LinearLayout = itemView.findViewById(R.id.container)
        val titleTxt: TextView = itemView.findViewById(R.id.titleTxt)
    }

    override fun onCreateViewHolder(
        inflater: LayoutInflater,
        parent: ViewGroup
    ): ViewHolder {
        return ViewHolder(inflater.inflate(R.layout.item_image_group, parent, false))
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        item: List<Image>
    ) {
        holder.apply {
            titleTxt.text = "图表信息"
            setRoundedBackground(container, getGroupColor(0), 10f)
            container.apply {
                removeViews(1, childCount - 1)
                for (image in item) {
                    addView(getImageView(image, context))
                }
            }
        }
    }

    private fun getImageView(item: Image, context: Context): ImageView {
        val imageUrl = item.imageUrl
        val image = ImageView(context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                100.dpToPx()
            )
            setPadding(0, 0, 0, 5.dpToPx())
        }

        Glide.with(context)
            .load(imageUrl)
//            .placeholder(R.drawable.placeholder_image)
//            .error(R.drawable.error_image)
            .into(image)

        image.setOnClickListener {
            val fragmentManager =
                (context as? androidx.fragment.app.FragmentActivity)?.supportFragmentManager
            if (fragmentManager != null) {
                val dialogFragment = ImageZoomDialogFragment.newInstance(imageUrl = imageUrl)
                dialogFragment.show(fragmentManager, "image_zoom_dialog")
            } else {
                // Handle case where FragmentManager couldn't be obtained
                // Log an error or show a Toast
            }
        }
        return image
    }

}