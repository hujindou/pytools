using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace TestRaiseEvent
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            var lst = Enumerable.Range(0, 150).ToList();

            Random rnd = new Random();

            var tmp = lst.Select(r => new
            {
                Column1 = r,
                Column2 = rnd.NextDouble() + "",
                Column3 = rnd.NextDouble() + "",
                Column4 = rnd.NextDouble() + "",
                Column5 = rnd.NextDouble() + "",
                Column6 = rnd.NextDouble() + "",
                Column7 = rnd.NextDouble() + "",
                Column8 = rnd.NextDouble() + "",
                Column9 = rnd.NextDouble() + "",
                Column10 = rnd.NextDouble() + "",
                Column11 = rnd.NextDouble() + "",
                Column12 = rnd.NextDouble() + "",
                Column13 = rnd.NextDouble() + "",
                Column14 = rnd.NextDouble() + "",
                Column15 = rnd.NextDouble() + "",
                Column16 = rnd.NextDouble() + "",
                Column17 = rnd.NextDouble() + "",
                Column18 = rnd.NextDouble() + "",
                Column19 = rnd.NextDouble() + "",
                Column20 = rnd.NextDouble() + "",
                Column21 = rnd.NextDouble() + "",
                Column22 = rnd.NextDouble() + "",
                Column23 = rnd.NextDouble() + "",
                Column24 = rnd.NextDouble() + "",
                Column25 = rnd.NextDouble() + "",
                Column26 = rnd.NextDouble() + "",
                Column27 = rnd.NextDouble() + "",
                Column28 = rnd.NextDouble() + "",
                Column29 = rnd.NextDouble() + "",
                Column30 = rnd.NextDouble() + "",
                Column31 = rnd.NextDouble() + "",
                Column32 = rnd.NextDouble() + "",
                Column33 = rnd.NextDouble() + "",
                Column34 = rnd.NextDouble() + "",
                Column35 = rnd.NextDouble() + "",
                Column36 = rnd.NextDouble() + "",
                Column37 = rnd.NextDouble() + "",
                Column38 = rnd.NextDouble() + "",
                Column39 = rnd.NextDouble() + "",
                Column40 = rnd.NextDouble() + "",
                Column41 = rnd.NextDouble() + "",
                Column42 = rnd.NextDouble() + "",
                Column43 = rnd.NextDouble() + "",
                Column44 = rnd.NextDouble() + "",
                Column45 = rnd.NextDouble() + "",
                Column46 = rnd.NextDouble() + "",
                Column47 = rnd.NextDouble() + "",
                Column48 = rnd.NextDouble() + "",
                Column49 = rnd.NextDouble() + "",
                Column50 = rnd.NextDouble() + "",
                Column51 = rnd.NextDouble() + "",
                Column52 = rnd.NextDouble() + "",
                Column53 = rnd.NextDouble() + "",
                Column54 = rnd.NextDouble() + "",
                Column55 = rnd.NextDouble() + "",
            });


            this.DataContext = vm;

            this.dg.ItemsSource = tmp;
        }

        ViewModel vm = new ViewModel();

        private int scmd = 0;
        private double htoff;
        private double vtoff;

        private double lhtoff;
        private double lvtoff;

        private void DG_ScrollViewer_PreviewTouchMove(object sender, TouchEventArgs e)
        {
            var sc = e.TouchDevice.Captured as ScrollViewer;

            if (this.scmd == 0)
            {
                if (sc != null)
                {
                    if (sc.HorizontalOffset != lhtoff)
                    {
                        //vm.PM = PanningMode.HorizontalOnly;
                        this.scmd = 1;
                        this.vtoff = sc.VerticalOffset;
                        //return;
                    }

                    if (sc.VerticalOffset != lvtoff && this.scmd == 0)
                    {
                        //vm.PM = PanningMode.VerticalOnly;
                        this.scmd = 2;
                        this.htoff = sc.HorizontalOffset;
                        //return;
                    }
                }
            }

            if (sc != null)
            {
                this.lvtoff = sc.VerticalOffset;
                this.lhtoff = sc.HorizontalOffset;
            }

        }

        private void DG_ScrollViewer_PreviewTouchDown(object sender, TouchEventArgs e)
        {
            //this.vm.PM = PanningMode.Both;
            this.scmd = 0;
        }

        private void DG_ScrollViewer_ScrollChanged(object sender, ScrollChangedEventArgs e)
        {
            if (this.scmd == 1)
            {
                ScrollViewer sc = sender as ScrollViewer;
                sc.ScrollToVerticalOffset(vtoff);
            }

            if (this.scmd == 2)
            {
                ScrollViewer sc = sender as ScrollViewer;
                sc.ScrollToHorizontalOffset(htoff);
            }
        }

        private void Dg_ManipulationBoundaryFeedback(object sender, ManipulationBoundaryFeedbackEventArgs e)
        {
            e.Handled = true;
        }
    }


    public class ViewModel : INotifyPropertyChanged
    {
        private PanningMode pm = PanningMode.Both;

        public event PropertyChangedEventHandler PropertyChanged;

        public string FirstName { get; set; }

        public PanningMode PM
        {
            get
            {
                return this.pm;
            }

            set
            {
                this.pm = value;
                this.OnPropertyChanged("PM");
            }
        }

        public void OnPropertyChanged(string propertyName) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
