class GaugeChart {
  constructor(element, params) {
      this._element = element;
      this._initialValue = params.initialValue;
      this._higherValue = params.higherValue;
      this._title = params.title;
      this._subtitle = params.subtitle;
      this._customTicks = params.customTicks || [0, 10, 20, 30, 40, 50, 60]; 
  }
  
  _buildConfig() {
      let element = this._element;
      
      return {
          value: this._initialValue,
          valueIndicator: {
              color: '#fff'
          },
          geometry: {
              startAngle: 180,
              endAngle: 360
          },
          scale: {
              startValue: 0,
              endValue: this._higherValue,
              customTicks: this._customTicks,
              tick: { 
                  length: 8
              },
              label: {
                  font: {
                      color: '#87959f',
                      size: 9,
                      family: '"Open Sans", sans-serif'
                  }
              }
          },
          title: {
              verticalAlignment: 'bottom',
              text: this._title,
              font: {
                  family: '"Open Sans", sans-serif',
                  color: '#fff',
                  size: 10
              },
              subtitle: {
                  text: this._subtitle,
                  font: {
                      family: '"Open Sans", sans-serif',
                      color: '#fff',
                      weight: 700,
                      size: 28
                  }
              }
          },
          onInitialized: function() {
              let currentGauge = $(element);
              let circle = currentGauge.find('.dxg-spindle-hole').clone();
              let border = currentGauge.find('.dxg-spindle-border').clone();

              currentGauge.find('.dxg-title text').first().attr('y', 48);
              currentGauge.find('.dxg-title text').last().attr('y', 28);
              currentGauge.find('.dxg-value-indicator').append(border, circle);
          }
      };
  }
  
  init() {
      $(this._element).dxCircularGauge(this._buildConfig());
  }

  update(value, subtitle) {
      let gaugeElement = $(this._element).dxCircularGauge('instance');
      gaugeElement.option('value', value);
      gaugeElement.option('title.subtitle.text', subtitle);
  }
}
